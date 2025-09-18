"""
Small Tkinter tool to annotate multi-constituent German compounds in CoNLL-U sentences.

Changes in this version:
- The multiword token line automatically gets an ID range based on the chosen start id and number of constituents.
- The span line is prefilled with the original compound token line, so the user can edit it.
- Constituent lines are empty, but all 10 columns are visible.
- Adjusted layout so that the fields fit into the scrollable canvas without exceeding window bounds.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re
import copy

column_names = ["ID","FORM","LEMMA","UPOS","XPOS","FEATS","HEAD","DEPREL","DEPS","MISC"]

# import and modification functions in background

# import user input
def import_conllu(text):
    lines = [ln for ln in text.strip().splitlines()]
    comments = [ln for ln in lines if ln.startswith('#')]
    token_lines = []
    for ln in lines:
        if ln.strip() == '' or ln.startswith('#'):
            continue
        cols = ln.split('\t')
        if len(cols) < 10:
            # pad columns to 10
            cols += ['_'] * (10 - len(cols))
        # token id
        id_field = cols[0]
        is_span = '-' in id_field
        token_lines.append({'raw': ln, 'cols': cols, 'is_span': is_span, 'id': id_field})
    return {'comments': comments, 'token_lines': token_lines}

# take token-id given by user and find correct token line
def find_token_index_by_id(token_lines, id_str):
    for tok_ind, tok in enumerate(token_lines):
        if tok['is_span']:
            continue
        if tok['id'] == str(id_str):
            return tok_ind
    return None

def format_token_line(cols):
    return '\t'.join(cols)

# integrate heads and dependency relations from user input
def update_heads_and_deps(token_lines, id_map):
    for tok in token_lines:
        if tok['is_span']:
            continue
        cols = tok['cols']
        head = cols[6]
        if head != '_' and head in id_map:
            cols[6] = id_map[head]
        deps = cols[8]
        if deps != '_' and deps.strip() != '':
            parts = deps.split('|') if '|' in deps else deps.split(';') if ';' in deps else deps.split(' ')
            newparts = []
            for part in parts:
                part = part.strip()
                if part == '':
                    continue
                if ':' in part:
                    core_rel, relation = part.split(':',1)
                    if core_rel in id_map:
                        core_rel = id_map[core_rel]
                    newparts.append(f"{core_rel}:{relation}")
                else:
                    if part in id_map:
                        newparts.append(id_map[part])
                    else:
                        newparts.append(part)
            cols[8] = '|'.join(newparts)
        tok['cols'] = cols

# functions to build the GUI for annotation

class CoBraAnnotator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CoBra Annotator")
        self.geometry("1200x750")

        self.create_widgets()
        self.token_data = None

    def create_widgets(self):
        # main frame
        top = ttk.Frame(self)
        top.pack(fill='x', padx=8, pady=8)
        # paste-field label
        ttk.Label(top, text='Paste the .conllu sentence here:').grid(row=0,column=0,sticky='w')
        # user input field
        self.input_text = tk.Text(self, width=80, height=18)
        self.input_text.pack(side='left', padx=8, pady=4, fill='both', expand=True)
        # middle console panel
        control_frame = ttk.Frame(self)
        control_frame.pack(side='left', fill='y', padx=8, pady=4)
        # user input fields for compound-start-id, constituent count and
        # selection of tok-id update / on middle console panel
        self.start_id_var = tk.StringVar(value='0')
        self.const_count_var = tk.IntVar(value=3)
        self.renumber_var = tk.BooleanVar(value=True)
        # labels and entry fields in middle console panel
        ttk.Label(control_frame, text='Start token id').pack()
        ttk.Entry(control_frame, textvariable=self.start_id_var, width=8).pack(pady=4)
        ttk.Label(control_frame, text='Number of constituents').pack()
        ttk.Spinbox(control_frame, from_=2, to=10, textvariable=self.const_count_var, width=6).pack(pady=4)
        ttk.Checkbutton(control_frame, text='Update token IDs after integration:', variable=self.renumber_var).pack(pady=6)
        # buttons in middle console panel
        ttk.Button(control_frame, text='Load fields', command=self.load_fields).pack(fill='x', pady=6)
        ttk.Button(control_frame, text='Apply and integrate', command=self.apply_changes).pack(fill='x', pady=6)
        ttk.Button(control_frame, text='Copy to clipboard', command=self.copy_to_clipboard).pack(fill='x', pady=6)
        ttk.Button(control_frame, text='Clear', command=self.clear_all).pack(fill='x', pady=6)
        # right console for new annotations
        right_frame = ttk.Frame(self)
        right_frame.pack(side='right', fill='both', expand=True, padx=8, pady=4)

        ttk.Label(right_frame, text='Editable fields for compound span and constituents:').pack(anchor='w')

        # scrollable area for fields
        self.fields_canvas = tk.Canvas(right_frame)
        self.fields_canvas.pack(fill='both', expand=True)

        self.fields_scroll_x = ttk.Scrollbar(right_frame, orient='horizontal', command=self.fields_canvas.xview)
        self.fields_scroll_x.pack(side='bottom', fill='x')
        self.fields_scroll_y = ttk.Scrollbar(right_frame, orient='vertical', command=self.fields_canvas.yview)
        self.fields_scroll_y.pack(side='right', fill='y')

        self.fields_canvas.configure(yscrollcommand=self.fields_scroll_y.set, xscrollcommand=self.fields_scroll_x.set)

        self.fields_inner = ttk.Frame(self.fields_canvas)
        self.fields_canvas.create_window((0,0), window=self.fields_inner, anchor='nw')
        self.fields_inner.bind('<Configure>', lambda e: self.fields_canvas.configure(scrollregion=self.fields_canvas.bbox('all')))
        # output field for integrated sentence in .conllu
        ttk.Label(right_frame, text='Annotated sentence (output):').pack(anchor='w', pady=(8,0))
        self.output_text = tk.Text(right_frame, width=60, height=12)
        self.output_text.pack(fill='both', expand=True)

        self.span_entries = {}
        self.const_entries = []
    # function for the clear all button
    def clear_all(self):
        confirm = messagebox.askyesno("Confirm Clear All", "Are you sure you want to clear all?")
        if confirm:
            self.input_text.delete('1.0', 'end')
            self.output_text.delete('1.0', 'end')
            for w in self.fields_inner.winfo_children():
                w.destroy()
            self.span_entries = {}
            self.const_entries = []
            self.token_data = None
            # reset defaults
            self.start_id_var.set('0')
            self.const_count_var.set(3)
            self.renumber_var.set(True)
    # generate annotation fields from entered start token
    def load_fields(self):
        raw = self.input_text.get('1.0','end').strip()
        # error messages
        if not raw:
            messagebox.showwarning('Input missing', 'Please paste a sentence in .conllu format into the input field.')
            return
        try:
            parsed = import_conllu(raw)
            self.token_data = parsed
        except Exception as e:
            messagebox.showerror('Input error', str(e))
            return

        start_id = self.start_id_var.get().strip()
        if not start_id.isdigit():
            messagebox.showerror('ID error', 'Start token id must be a positive integer.')
            return
        n_const = int(self.const_count_var.get())

        idx = find_token_index_by_id(self.token_data['token_lines'], start_id)
        if idx is None:
            messagebox.showerror('Token not found', f'Token id {start_id} not found.')
            return

        orig_token = self.token_data['token_lines'][idx]

        # propose ID range for span
        start_num = int(start_id)
        end_num = start_num + n_const - 1
        id_range = f"{start_num}-{end_num}"
        # clear middle console when loading annotation fields
        for w in self.fields_inner.winfo_children():
            w.destroy()
        self.span_entries = {}
        self.const_entries = []

        # Span annotation fields
        span_frame = ttk.LabelFrame(self.fields_inner, text='Compound span row')
        span_frame.pack(fill='x', pady=4, padx=4)
        for i_col, colname in enumerate(column_names):
            ttk.Label(span_frame, text=colname).grid(row=0, column=i_col, sticky='w')
        entries_row = {}
        # pre-fill with original token annotation
        for i_col, colname in enumerate(column_names):
            ent = ttk.Entry(span_frame, width=12)
            ent.grid(row=1, column=i_col, padx=2, pady=2)
            if colname == 'ID':
                ent.insert(0, id_range)
            else:
                ent.insert(0, orig_token['cols'][i_col] if i_col < len(orig_token['cols']) else '_')
            entries_row[colname] = ent
        self.span_entries = entries_row

        # Constituent frames (empty)
        for j_range, j in enumerate(range(n_const)):
            fr = ttk.LabelFrame(self.fields_inner, text=f'Constituent {j+1}')
            fr.pack(fill='x', pady=4, padx=4)
            entrow = {}
            # add labels for column-names
            for i_col, col in enumerate(column_names):
                ttk.Label(fr, text=col).grid(row=0, column=i_col, sticky='w')
                # add annotation fields
            for i_col, col in enumerate(column_names):
                entry = ttk.Entry(fr, width=12)
                entry.grid(row=1, column=i_col, padx=2, pady=2)
                # pre-fill with new tok ids
                if col == 'ID':
                    entry.insert(0, str(start_num + j_range))
                    entrow[col] = entry
                # pre-fill with inherited upos, xpos and feats parse
                elif col == "UPOS" or col == "XPOS" or col == "FEATS" or col == "DEPS":
                    entry.insert(0, orig_token['cols'][i_col])
                    entrow[col] = entry
                else:
                    entrow[col] = entry
                # entrow[col] = entry

            self.const_entries.append({'frame': fr, 'entries': entrow})

        self.output_text.delete('1.0','end')
        self.output_text.insert('1.0', raw)
    # apply changes to the output .conllu
    def apply_changes(self):
        if self.token_data is None:
            messagebox.showwarning('No data', 'Load fields first.')
            return

        new_token_lines = copy.deepcopy(self.token_data['token_lines'])

        start_id = self.start_id_var.get().strip()
        # start id = idx
        idx = find_token_index_by_id(new_token_lines, start_id)
        if idx is None:
            messagebox.showerror('Not found', 'Start token not found. Reload fields and try again.')
            return
        # collect entries
        span_cols = []
        for colname in column_names:
            val = self.span_entries[colname].get().strip()
            if val == '' or val is None:
                missing = messagebox.askyesno(colname + ' missing', colname +' missing in span row, do you want to leave ' + colname + ' empty? Click no to continue annotation or yes to parse output.')
                if not missing:
                    return
            span_cols.append(val if val != '' else '_')
        span_line = {'cols': span_cols, 'is_span': True, 'id': span_cols[0]}

        const_dicts = []
        for conent_ind, con_ent in enumerate(self.const_entries):
            cols = []
            for cname in column_names:
                val = con_ent['entries'][cname].get().strip()
                if val == '' or val is None:
                    missing = messagebox.askyesno(cname + ' missing', cname +' missing in constituent ' + str(conent_ind + 1) + ', do you want to leave ' + cname + ' empty? Click no to continue annotation or yes to parse output.')
                    if not missing:
                        return
                cols.append(val if val != '' else '_')
            const_dicts.append({'cols': cols, 'is_span': False, 'id': int(cols[0])})
        # remove old start-token-line, add new start-token-line and constituen lines
        new_token_lines.pop(idx)
        new_token_lines.insert(idx, span_line)
        for j, con_dict_entry in enumerate(const_dicts):
            new_token_lines.insert(idx + 1 + j, con_dict_entry)
        # update ids
        if self.renumber_var.get():
            old_ids = [t['id'] for t in new_token_lines]
            id_map = {}
            newnum = 1
            for old_ind, old in enumerate(old_ids):
                # spans
                if type(old) == str and '-' in old:
                    id_map[old] = old
                # individual new const tok ids
                else:
                    # bc of new const ids inserted the newnum counter will be + const-count minus 1 from last new tok
                    # thereby upping all subsequent tok ids by the respective amount
                    # first check if old is a span unrelated to current compound
                    if type(old_ids[old_ind-1]) == str and '-' in old_ids[old_ind-1] and not old_ids[old_ind-1].startswith(start_id + '-'):
                        span_match = re.match(r"(\d+)-(\d+)$", old_ids[old_ind-1])
                        a = ''
                        b = ''
                        if span_match:
                            a, b = span_match.group(1), span_match.group(2)
                        diff_span = int(b)-int(a)
                        id_map[old] = str(newnum+1+diff_span)
                        newnum += (2+diff_span)
                    else:
                        id_map[old] = str(newnum)
                        newnum += 1
            for t in new_token_lines:
                if not t['is_span']:
                    if t['id'] in id_map:
                        t['id'] = id_map[t['id']]
                        t['cols'][0] = t['id']
                # matching spans
                else:
                    span_match = re.match(r"(\d+)-(\d+)$", t['id'])
                    a = ''
                    b = ''
                    if span_match:
                        a, b = span_match.group(1), span_match.group(2)
                    # identify current comp span
                    if int(a) == int(start_id):
                        t['cols'][0] = t['id']
                        # identify all other spans unrelated to comp span
                    else:
                        # m = re.match(r"(\d+)-(\d+)$", t['id'])
                        # if m:
                        #     a,b = m.group(1), m.group(2)
                            # na = id_map.get(a, a)
                            # nb = id_map.get(b, b)
                        t['id'] = f"{int(a)+(int(self.const_count_var.get())-1)}-{int(b)+(int(self.const_count_var.get())-1)}"
                        t['cols'][0] = t['id']
            # update_heads_and_deps(new_token_lines, id_map)
            # update all subsequent heads if they refer to toks after new span
            for  t in new_token_lines[idx+(int(self.const_count_var.get())-1):]:
                cols = t['cols']
                head = cols[6]
                if head != '_' and int(head) > idx+(int(self.const_count_var.get())-1):
                    t['cols'][6] = str(int(head)+(int(self.const_count_var.get())-1))


        out_lines = []
        for c in self.token_data['comments']:
            out_lines.append(c)
        for t in new_token_lines:
            out_lines.append(format_token_line(t['cols']))

        final_text = '\n'.join(out_lines)
        self.output_text.delete('1.0','end')
        self.output_text.insert('1.0', final_text)

    def copy_to_clipboard(self):
        txt = self.output_text.get('1.0','end').strip()
        if not txt:
            messagebox.showwarning('Nothing to copy', 'There is no output to copy. Apply changes first.')
            return
        self.clipboard_clear()
        self.clipboard_append(txt)
        messagebox.showinfo('Copied', 'Annotated sentence copied to clipboard.')

if __name__ == '__main__':
    app = CoBraAnnotator()
    app.mainloop()
