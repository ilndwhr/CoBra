"""
This tool provides a lightweight GUI for annotating and editing three-constituent German compounds in CoNLL-U Format developed along the CoBra-resource.
It is designed to extend the Universal Dependencies (UD) format with new multiword-token spans for German multi-constituent compounds (similar to MWTs but on compond-constituent-level).

"""
from base64 import b64decode
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re
import copy

column_names = ["ID","FORM","LEMMA","UPOS","XPOS","FEATS","HEAD","DEPREL","DEPS","MISC"]
# Define images
onbutton = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAICAIAAAB/FOjAAAABgGlDQ1BzUkdCIElFQzYxOTY2LTIuMQAAKJF1kc8rRFEUxz8zyK8RxYKyeGlYIT9qYqOMhJo0jVEGmzfPmxk1P17vzSTZKltFiY1fC/4CtspaKSIla7bEBj3neWokc2/3ns/93nNO554L3mhay1jlPZDJ5s3IWFCZic0qlU/UUC1ToUXVLGM4HA5Rcrzd4HHsVZeTq7Tfv6N2Qbc08FQJD2mGmRceFw4t5Q2HN4WbtJS6IHws3GlKgcLXjh53+dHhpMsfDpvRyAh4G4SV5C+O/2ItZWaE5eX4M+mC9lOP8xKfnp2eEtsmqxWLCGMEpRcTjDJCgF4GZQ/QRR/dcqJEfM93/CQ5idVkN1jGZJEkKfJ0ilqQ7LrYhOi6zDTLTv//9tVK9Pe52X1BqHiw7Zd2qNyAz3Xbft+37c8DKLuHs2wxPrcHA6+irxc1/y7Ur8LJeVGLb8HpGjTfGaqpfktlsryJBDwfQV0MGi+hZs7t2c89h7cQXZGvuoDtHegQ//r5LzmGZ9GMJUeIAAAACXBIWXMAAD2EAAA9hAHVrK90AAAA0klEQVQYlWP89/9f3fPps84v+3nzEyMTI7sWP4skJwM24MlnPU22ilklz7R5W//nTU/+PP/+59n3H5c+MAuysYhyYGq48/OxKKsg848ovtsrzjP8R0j8fviV00iIkZkRU8/Hv1+YLt+99v/vf2TR/z///nn1A6urHv56zsTBxIZVDiv4+e8Xk6aSOiMLiu2MHMwsYlj8wMDAoMQuw5QqH8btKIEQY2LkcZNkZGPCqsGZ15x5Wfv8fxKs50UfMHEws8px8zhLsinwYFVtx2PUKJkJAK7HQpzkHyDqAAAAAElFTkSuQmCC"
offbutton = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAICAIAAAB/FOjAAAABgGlDQ1BzUkdCIElFQzYxOTY2LTIuMQAAKJF1kc8rRFEUxz8zyK8RxYKyeGlYIT9qYqOMhJo0jVEGmzfPmxk1P17vzSTZKltFiY1fC/4CtspaKSIla7bEBj3neWokc2/3ns/93nNO554L3mhay1jlPZDJ5s3IWFCZic0qlU/UUC1ToUXVLGM4HA5Rcrzd4HHsVZeTq7Tfv6N2Qbc08FQJD2mGmRceFw4t5Q2HN4WbtJS6IHws3GlKgcLXjh53+dHhpMsfDpvRyAh4G4SV5C+O/2ItZWaE5eX4M+mC9lOP8xKfnp2eEtsmqxWLCGMEpRcTjDJCgF4GZQ/QRR/dcqJEfM93/CQ5idVkN1jGZJEkKfJ0ilqQ7LrYhOi6zDTLTv//9tVK9Pe52X1BqHiw7Zd2qNyAz3Xbft+37c8DKLuHs2wxPrcHA6+irxc1/y7Ur8LJeVGLb8HpGjTfGaqpfktlsryJBDwfQV0MGi+hZs7t2c89h7cQXZGvuoDtHegQ//r5LzmGZ9GMJUeIAAAACXBIWXMAAD2EAAA9hAHVrK90AAAAxElEQVQYlWP8+fdf1sXHO15+YsAGfj1//v3q1f///nGqq2fYGjVqSrIsffwOl+pvV66837yZ4f9/BgaGr2fOTH71Si3Bn2n9849YVf//9evjrl0Q1RDwaf/+ZTceMz349hOrht8vX/778QPFiD9/Ll6/w/Tr33+sGrACTmYmJiUudqxyrBISTJycyCKMLCzaGipMzmK8WDUwsrIKuLszMjHB+Iz8zs5p2nKMn3//TT3/6PDbL7h88v3aNUiwFtoZVqiJAwD0GVjY1/MMFgAAAABJRU5ErkJggg=="
small_icon_data = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABgGlDQ1BzUkdCIElFQzYxOTY2LTIuMQAAKJF1kc8rRFEUxz8zyK8RxYKyeGlYIT9qYqOMhJo0jVEGmzfPmxk1P17vzSTZKltFiY1fC/4CtspaKSIla7bEBj3neWokc2/3ns/93nNO554L3mhay1jlPZDJ5s3IWFCZic0qlU/UUC1ToUXVLGM4HA5Rcrzd4HHsVZeTq7Tfv6N2Qbc08FQJD2mGmRceFw4t5Q2HN4WbtJS6IHws3GlKgcLXjh53+dHhpMsfDpvRyAh4G4SV5C+O/2ItZWaE5eX4M+mC9lOP8xKfnp2eEtsmqxWLCGMEpRcTjDJCgF4GZQ/QRR/dcqJEfM93/CQ5idVkN1jGZJEkKfJ0ilqQ7LrYhOi6zDTLTv//9tVK9Pe52X1BqHiw7Zd2qNyAz3Xbft+37c8DKLuHs2wxPrcHA6+irxc1/y7Ur8LJeVGLb8HpGjTfGaqpfktlsryJBDwfQV0MGi+hZs7t2c89h7cQXZGvuoDtHegQ//r5LzmGZ9GMJUeIAAAACXBIWXMAAD2EAAA9hAHVrK90AAABk0lEQVQokY2QvS8DcRjHn99dz2lPtSep0IF4ayJqwmYQk0EkDCKxi9m/ILEwisFALBKLmMTQhEGMgiKIlxLak2vr2nvpXe/u9xjaFIlwn+3J83yePN+HOKZZNgy/KII3GJbnk9tbJUUCRE8CAIi9kf3l6b2lKa8C6+e0ks3ZH0XpvtZA1ykpUvH9QZVT3wWCiACQf0k+nexIN8ehaIwwrJLNGEXFpTRYz+Q0t6MrNjCzGBCjX0KFXOr87nDDsXSXcHX1DYSAWZTzmSfLwWhn38jcGhDyQ/gFxLujzcvEFs+R+PhC++AE809GQrqGZ/2CIKuunEpWQ/8Ny/Hh1p5IkAVb9yQg0oL8KquuoX4AgO/XCUKqi8pG4fpgVVXkcIAJt3T+EDJXRzeJdUvLUdeGusag2GzqBTUvaSYVBVYvQzQ+CrW3OpaRWJlkfHyke0iTn7PpRx+hlo2Wg2KoQYh09I/NN7X1Vw5ARMw+np7tLtmmXimpYxvKu5K+1fNvSCl+oyrkni+csokeqJ2k+3jh348BwCdrQQqylQue3gAAAABJRU5ErkJggg=="
large_icon_data = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAABgGlDQ1BzUkdCIElFQzYxOTY2LTIuMQAAKJF1kc8rRFEUxz8zyK8RxYKyeGlYIT9qYqOMhJo0jVEGmzfPmxk1P17vzSTZKltFiY1fC/4CtspaKSIla7bEBj3neWokc2/3ns/93nNO554L3mhay1jlPZDJ5s3IWFCZic0qlU/UUC1ToUXVLGM4HA5Rcrzd4HHsVZeTq7Tfv6N2Qbc08FQJD2mGmRceFw4t5Q2HN4WbtJS6IHws3GlKgcLXjh53+dHhpMsfDpvRyAh4G4SV5C+O/2ItZWaE5eX4M+mC9lOP8xKfnp2eEtsmqxWLCGMEpRcTjDJCgF4GZQ/QRR/dcqJEfM93/CQ5idVkN1jGZJEkKfJ0ilqQ7LrYhOi6zDTLTv//9tVK9Pe52X1BqHiw7Zd2qNyAz3Xbft+37c8DKLuHs2wxPrcHA6+irxc1/y7Ur8LJeVGLb8HpGjTfGaqpfktlsryJBDwfQV0MGi+hZs7t2c89h7cQXZGvuoDtHegQ//r5LzmGZ9GMJUeIAAAACXBIWXMAAD2EAAA9hAHVrK90AAAD80lEQVRIibWVz28bRRTH3+wP79retRN741hJnDR12kZNQWkaoCoNqIJDoqiKVPXS8uOAVHEB+k9wAnHhwg0BqsSFA79CqThFVOLQ1KE0bYrIL8e1nTTrZL1e7++d4bDBoc6vVtp8LzPzZt77zHuzM4sIIXatFhJFOBxRAFCanl65ffuQAEAIUZaXvzx3ri7L5BCECCEAcP/GjeU73x2fuMgJibbscDSZCSqBLYCtV3/7ZAIAbBezDHXiwnvHXn83EADlN+rqAgBgQmbzSkW1qqVHgUTfBgCAi8mt3OpQNiHFOKUYGIDxGz4mRYSWsTPIH1raRmHmZmZwFBDa6WOqsibnzZrs2abnmNi1o8lMsvd0KBLfuXjrDADAs83H934tP5zayN8jGANANNmV6H4xmuxyrbpt1BxDNdX1jfIScnUA0CwscJSfelXHqdZo9vzVY6+907SnbUBD6trC/Z8+Ux4/bLKvVt1UjClsOCmRCYfQg6I90BkCgJm8daorxNIIAI68cmlg7KMDAABACC7kJv+Z+tpU5YZR0XE8TFkuYWhgKKTbOBKiNAubDpEEGgAcjxgOeWn8/b6Rtw4A+MKus5L7ubI0Q7BHsEfRDB9PhePtvCgBQthzPNsszf2+sTgNAKqB55/Yg908w7AXrn/Lx6SDAc+oQm5y5odP11W3Pcb49e89e/nk6Af+LLWf67MpMzTec3o0HWcap1vITfqfSTAAAOh/4xpFs37fw6DV9XqlECSAE5PxzhNVA88WrYUnNkODujrvTzGBAABAkHriK7PxTs4fGtU1vxNMBgCgb5b/P0QU7XcCy0CrFOSaV6q60RDV0coEDDCUNasmSyItif/F5SJ+J4AS6ZvlP766jvFT96k1c2qLtK9nyTXrNBcJhUU2HNs1tFKcm731hVNbdz2yJDvpOBMPU5yYFKTuPQGE4Pmpbwp/3jSUtYaRYlhOSPKixItJTkjom2Wl9MjSFIRAs7DtkkSUzqbYQsWlEXS8MNhw3AXw4JfP83e+bzJi1zGU1fxKMRWjDZswNLA0KlfdjhZG4Ki7ZTMRpRkK9baxFMNlX72yvbOmQPVKYWX6x72KZnsEAFQT1y0CABXN8+29bazhEACItHYMX/k4lu7bMwN5MUcI9mvSfeZiZmgcO7apVTbzf8mLd7vQIhDSJtD+s9OdYAEgFG05fjQrpI4mMifT/SOIfipmM0ApzgFCPcMTfSNvN55cAEj3nwcAx9RMVbZ1xa5v2roabmmPpft4UYK91Qyolv4+8vKlgbEPd13N8gLLC/uE26nmM+Bjbf1vXnuuEM8H6D17mWb5AAHNfzTHUHe9U4EBCMaICuyJBYB/AYK3GvaVRxKXAAAAAElFTkSuQmCC"

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
        small_icon = tk.PhotoImage(data=b64decode(small_icon_data))
        large_icon = tk.PhotoImage(data=b64decode(large_icon_data))
        self.iconphoto(False, large_icon, small_icon)

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
        # check button for mode swtich between annotation of existing span and creation of new span
        # self.annotate_existing_var = tk.BooleanVar(value=False)
        # ttk.Checkbutton(
        #     control_frame,
        #     text="Annotate existing token-span",
        #     variable=self.annotate_existing_var
        # ).pack(pady=6)
        self.annotate_existing_var = False
        # Create Label
        self.toggleLabel = ttk.Label(control_frame,
            text="Create new token-span")
        self.toggleLabel.pack(pady=6)
        # create toggle images
        self.on = tk.PhotoImage(data=b64decode(onbutton))
        self.off = tk.PhotoImage(data=b64decode(offbutton))
        # Create toggle button
        self.on_button = ttk.Button(control_frame, image=self.on, command=self.switch)
        self.on_button.pack(pady=6)

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

    # toggle switch function
    def switch(self):
        # toggle on or off
        if self.annotate_existing_var:
            self.on_button.config(image=self.on)
            self.toggleLabel.config(text="Create new token-span")
            # self.on_button.config(image=self.off)
            # self.toggleLabel.config(text="Annotate existing token-span")
            self.annotate_existing_var = False
        else:
            self.on_button.config(image=self.off)
            self.toggleLabel.config(text="Annotate existing token-span")
            # self.on_button.config(image=self.on)
            # self.toggleLabel.config(text="Create new token-span")
            self.annotate_existing_var = True
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

        start_num = int(start_id)
        n_const = int(self.const_count_var.get())
        end_num = start_num + n_const - 1

        # clear previous UI
        for w in self.fields_inner.winfo_children():
            w.destroy()
        self.span_entries = {}
        self.const_entries = []

        # if self.annotate_existing_var.get():
        if self.annotate_existing_var:
            # annotate existing span
            span_frame = ttk.LabelFrame(self.fields_inner, text='Existing tokens to annotate')
            span_frame.pack(fill='x', pady=4, padx=4)

            for i_col, colname in enumerate(column_names):
                ttk.Label(span_frame, text=colname).grid(row=0, column=i_col, sticky='w')

            # load existing tokens directly
            for j, tok_idx in enumerate(range(start_num, end_num + 1)):
                token = next((t for t in self.token_data['token_lines'] if t['id'] == str(tok_idx)), None)
                if token is None:
                    messagebox.showerror('Token missing', f'Token ID {tok_idx} not found in input.')
                    return

                fr = ttk.LabelFrame(self.fields_inner, text=f'Token {tok_idx}')
                fr.pack(fill='x', pady=4, padx=4)
                entrow = {}
                for i_col, col in enumerate(column_names):
                    ttk.Label(fr, text=col).grid(row=0, column=i_col, sticky='w')
                    entry = ttk.Entry(fr, width=12)
                    entry.grid(row=1, column=i_col, padx=2, pady=2)
                    # leave head, deprel and misc empty for annotation
                    if col not in ("HEAD", "DEPREL", "MISC"):
                        entry.insert(0, token['cols'][i_col])
                    entrow[col] = entry
                self.const_entries.append({'frame': fr, 'entries': entrow})
        # new-span setting
        else:
            id_range = f"{start_num}-{end_num}"
            span_frame = ttk.LabelFrame(self.fields_inner, text='Compound span row')
            span_frame.pack(fill='x', pady=4, padx=4)
            for i_col, colname in enumerate(column_names):
                ttk.Label(span_frame, text=colname).grid(row=0, column=i_col, sticky='w')
            entries_row = {}
            for i_col, colname in enumerate(column_names):
                ent = ttk.Entry(span_frame, width=12)
                ent.grid(row=1, column=i_col, padx=2, pady=2)
                if colname == 'ID':
                    ent.insert(0, id_range)
                else:
                    ent.insert(0, orig_token['cols'][i_col] if i_col < len(orig_token['cols']) else '_')
                entries_row[colname] = ent
            self.span_entries = entries_row

            # create empty const frames
            for j_range, j in enumerate(range(n_const)):
                fr = ttk.LabelFrame(self.fields_inner, text=f'Constituent {j + 1}')
                fr.pack(fill='x', pady=4, padx=4)
                entrow = {}
                # create entry rows according to user settings
                for i_col, col in enumerate(column_names):
                    ttk.Label(fr, text=col).grid(row=0, column=i_col, sticky='w')
                    entry = ttk.Entry(fr, width=12)
                    entry.grid(row=1, column=i_col, padx=2, pady=2)
                    if col == 'ID':
                        entry.insert(0, str(start_num + j_range))
                    elif col in ("UPOS", "XPOS", "FEATS", "DEPS"):
                        entry.insert(0, orig_token['cols'][i_col])
                    entrow[col] = entry
                self.const_entries.append({'frame': fr, 'entries': entrow})
        # load un-annotated user input into the output box to be updated later
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

        # early return for existing-span-mode without renumbering
        # all the following span functionalities get skipped bc not necessary
        # if self.annotate_existing_var.get():
        if self.annotate_existing_var:
            for condictent_ind, con_dict_entry in enumerate(self.const_entries):
                cols = []
                for cname in column_names:
                    val = con_dict_entry['entries'][cname].get().strip()
                    # confimr missing values
                    if val == '' or val is None:
                        missing = messagebox.askyesno(cname + ' missing', cname + ' missing in constituent ' + str(
                            condictent_ind + 1) + ', do you want to leave ' + cname + ' empty? Click no to continue annotation or yes to parse output.')
                        if not missing:
                            return
                    cols.append(val if val != '' else '_')
                # find token in original by ID
                target_id = cols[0]
                for tok in new_token_lines:
                    if not tok['is_span'] and tok['id'] == target_id:
                        tok['cols'] = cols
                        break

            # prepare for output/ Ids/haeds don't get updated here
            out_lines = []
            for c in self.token_data['comments']:
                out_lines.append(c)
            for t in new_token_lines:
                out_lines.append(format_token_line(t['cols']))
            # show outputs
            final_text = '\n'.join(out_lines)
            self.output_text.delete('1.0', 'end')
            self.output_text.insert('1.0', final_text)
            return

        # collect entries
        span_cols = []
        for colname in column_names:
            print(colname)
            val = self.span_entries[colname].get().strip()
            # confimr missing values
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
                # confimr missing values
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
                # existing spans
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
                # map non-spans
                if not t['is_span']:
                    if t['id'] in id_map:
                        t['id'] = id_map[t['id']]
                        t['cols'][0] = t['id']
                # matching spans with updated const length
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

        # prepare for output
        out_lines = []
        for c in self.token_data['comments']:
            out_lines.append(c)
        for t in new_token_lines:
            out_lines.append(format_token_line(t['cols']))
        # show output
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
