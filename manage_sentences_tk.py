import tkinter as tk

from tkinter import ttk, filedialog, simpledialog, messagebox

from Galutils import *

import hunspell




def get_spacy_pos(s):
    equivalence = dict([('advervio', 'ADV'),
                        ('adverbio', 'ADV'),
                        ('pretérito', 'VERB'),
                        ('presente', 'VERB'),
                        ('subxuntivo', 'VERB'),
                        ('futuro', 'VERB'),
                        ('locución_adverbial', 'ADV'),
                        ('abreviatura', 'PROPN'),
                        ('adxectivo', 'ADJ'),
                        ('contracción', 'ADP'),
                        ('conxunción', 'CONJ'),
                        ('interxección', 'INTJ'),
                        ('nome propio', 'PROPN'),
                        ('pronome', 'PRON'),
                        ('participio', 'VERB'),
                        ('preposición', 'ADP'),
                        ('sigla', 'PROPN'),
                        ('símbolo', 'SYM'),
                        ('verbo', 'VERB'),
                        ('pónimo', 'PROPN'),
                        ('nom', 'NOUN'),
                        ('num', 'NUM'),
                        ('subst', 'NOUN'),
                        ])

    for pat in equivalence:
        if pat in s:
            return equivalence[pat]
    return 'UNK'


def decode_hunspell(huns):
    '''
    get hunspell response (huns) in plain text
    '''
    huns = [clean for item in huns if not '[n-gram' in (clean := item.decode())]

    res = {}
    for cad in huns:
        st = po = ''
        st = re.findall(r'st:(.*?)\W|st:(.*?)$', cad)
        po = [item for item in unravel(re.findall(r'po:(.*?)\W|po:(.*?)$', cad)) if item]
        if not po:
            po = [item for item in unravel(re.findall(r'is:(.*?)\W|is:(.*?)$', cad)) if item]

        if st and po and st[0][0]:
            st = st[0][0].split()[0].strip()
            res[st] = res.get(st, []) + po
    return res


def hun2spacy(lemma,dic):
    return {key.strip(): set([v for i in val if (v := get_spacy_pos(i)) != 'UNK']) for key, val in
            decode_hunspell(dic.analyze(lemma)).items()}

def get_warning(dic,token, lemma, pos):
    if not dic or pos in ['PUNCT']:
        return

    hs = hun2spacy(token,dic)
    k = pos.replace('AUX', 'VERB').replace('CCONJ', 'CONJ').replace('SCONJ', 'CONJ')
    if lemma in hs.keys():

        if not k in hs[lemma]:
            return 'red'  # .append(f'\tToken ({j}): {toks[j]} POS unrecognized for HS lemma {lemma[j]}, alternatives {hs[lemma[j]]}')
    else:
        alts = [(key, val) for key, val in hs.items() if k in val]
        if alts:
            return 'orange'  # .append(f'\tToken ({j}): {toks[j]} lemma unknown by HS; proposed lemmas based in POS:{alts}')
        else:
            return 'brown'  # .append(f'\tToken ({j}): {toks[j]}, lemma {lemma[j]} unknown by HS')

postag = ['ADJ',
          'ADP',
          'ADV',
          'AUX',
          'CCONJ',
          'CONJ',
          'DET',
          'NOUN',
          'NUM',
          'PRON',
          'PROPN',
          'PUNCT',
          'SCONJ',
          'SYM',
          'VERB',
          'X']

class MyDialog(tk.simpledialog.Dialog):
    '''
    custom simple dialog with its own widgets and buttons, from https://code-maven.com/slides/python/tk-customized-simple-dialog
    '''
    def __init__(self, parent, sentence):
        self.sent = sentence

        super().__init__(parent,'Edit sentence')

    def body(self, frame):
        # print(type(frame)) # tkinter.Frame
        self.my_text_box = tk.Text(frame, width=80)
        self.my_text_box.insert('end',self.sent)
        self.my_text_box.pack()

        return frame

    def ok_pressed(self):
        # print("ok")
        self.sent = self.my_text_box.get('1.0','end')

        self.destroy()

    def cancel_pressed(self):
        # print("cancel")
        self.sent=None
        self.destroy()


    def buttonbox(self):
        self.ok_button = tk.Button(self, text='OK', width=5, command=self.ok_pressed)
        self.ok_button.pack(side="left")
        cancel_button = tk.Button(self, text='Cancel', width=5, command=self.cancel_pressed)
        cancel_button.pack(side="right")
        self.bind("<Return>", lambda event: self.ok_pressed())
        self.bind("<Escape>", lambda event: self.cancel_pressed())





class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    from https://stackoverflow.com/questions/16188420/tkinter-scrollbar-for-frame
    """

    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor='nw')

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion=(0,0,size[0],size[1]))
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', _configure_canvas)


class WindowSentence():
    def __init__(self, sentences=None, corpus=None, data_path=None):

        self.path = data_path

        self.corpus = corpus
        self.sents = sentences
        self.index = 0

        self.root = tk.Tk()

        self.root.geometry('800x400')

        control_frame = ttk.Frame(self.root)

        self.index_sv = tk.StringVar(control_frame, value=f'{self.index + 1}/{len(self.sents) if self.sents else 0}')
        label_indx = ttk.Label(control_frame, textvariable=self.index_sv)
        label_indx.grid(column=1, row=0)
        button_mas = ttk.Button(control_frame, text='+', command=self.index_up)
        button_mas.grid(column=2, row=0)
        button_menos = ttk.Button(control_frame, text='-', command=self.index_down)
        button_menos.grid(column=0, row=0)

        self.goto_sv = tk.StringVar(control_frame, value=f'{self.index + 1}')
        entry_goto = ttk.Entry(control_frame, textvariable=self.goto_sv, justify='right', width=6)
        entry_goto.grid(column=3, row=0)
        button_goto = ttk.Button(control_frame, text='GoTo', command=self.goto_page)
        button_goto.grid(column=4, row=0)

        button_delete = ttk.Button(control_frame, text='Delete sentence', command=self.delete)
        button_delete.grid(column=0, row=1)
        button_load = ttk.Button(control_frame, text='Load sentences', command=self.load_sents)
        button_load.grid(column=3, row=1)
        button_exit = ttk.Button(control_frame, text='Save&Exit', command=self.exit)
        button_exit.grid(column=4, row=1)

        self.warnings=tk.IntVar()
        #activate by default
        self.warnings.set(1)
        check_warning=ttk.Checkbutton(control_frame, text='warnings', variable=self.warnings)
        check_warning.grid(column=5,row=0)

        self.filter=tk.IntVar()
        check_filter=ttk.Checkbutton(control_frame, text=' Filter',variable=self.filter)
        check_filter.grid(column=6,row=0)

        radio_frame=ttk.Frame(control_frame)
        self.radio=tk.IntVar()
        radio_token=ttk.Radiobutton(radio_frame,text='Token',variable=self.radio,value=0)
        radio_token.pack(side='left')
        radio_lemma = ttk.Radiobutton(radio_frame, text='Lemma', variable=self.radio, value=1)
        radio_lemma.pack(side='left')
        radio_pos = ttk.Radiobutton(radio_frame, text='POS', variable=self.radio, value=2)
        radio_pos.pack(side='left')
        self.text_filter=tk.StringVar()
        entry_filter=ttk.Entry(radio_frame,textvariable=self.text_filter)
        entry_filter.pack(side='top')
        radio_frame.grid(column=5,columnspan=2,row=1)



        control_frame.pack(fill='both')
        if not self.path:
            self.load_dir(title='Data directory')

        if not self.sents:
            self.load_sents(auto=False)
            self.index_sv.set(f'{self.index + 1}/{len(self.sents)}')

            if not self.corpus:
                self.load_corpus()

        self.root.title(self.path.stem)
        self.create_frame()
        self.run()

    def exit(self):
        file = filedialog.asksaveasfilename(initialdir=self.path,
                                            title='Save changes...',
                                            filetypes=(('pickle files', '*.pkl'), ("all files", "*.*")))
        if file:
            pickle_var(file, self.sents)
            self.root.destroy()

    def load_sents(self, auto=True):
        file = self.load_file(initialdir=self.path,
                              title='Load sentences...',
                              filetypes=(('pickle files', '*.pkl'), ("all files", "*.*"))
                              )
        self.sents = pickle_var(file)
        self.index = 0
        if auto:
            self.index_sv.set(f'{self.index + 1}/{len(self.sents)}')
            self.frame.destroy()
            self.create_frame()

    def load_corpus(self):
        file = self.load_file(initialdir=self.path,
                              title='Load corpuscle...',
                              filetypes=(('pickle files', '*.pkl'), ("all files", "*.*"))
                              )
        self.corpus = pickle_var(file)

    def load_dir(self, title=''):
        file = filedialog.askdirectory(initialdir='',
                                       title=title,
                                       )
        self.path = Path(file)

    def load_file(self, initialdir='', title='', filetypes=()):
        initialdir = initialdir if initialdir else self.path

        return filedialog.askopenfilename(initialdir=initialdir,
                                          title=title,
                                          filetypes=filetypes
                                          )

    def pretty_print(self,sent,lenght=80):
        if len(sent)<lenght:
            return sent
        cad = []
        chunk = ''
        for token in sent.split():
            if len(chunk + ' ' + token) > lenght:
                cad.append(chunk)
                chunk = token
            else:
                chunk += ' ' + token
        cad.append(chunk)
        return '\n'.join(cad)


    def EditSentence(self):

        dialog = MyDialog(parent=self.root,sentence=self.pretty_print(self.sents[self.index][0]))
        if dialog.sent:
            sent=dialog.sent.replace('\n',' ').strip()
            sentence=self.corpus.model_predict(sent)
            if len(sentence)==len(self.sents[self.index][1]):
                new_toks=tuple([tuple([item[0],old[1],old[2]]) for item,old in zip(sentence,self.sents[self.index][1])])
                self.sents[self.index]=(sent,new_toks)
            else:
                self.sents[self.index]=(sent,[(t,p,l) for t,p,l in sentence])
            self.frame.destroy()
            self.create_frame()

    def EditToken(self,token=''):
        if hspell:
            messagebox.showinfo(self.root,message=hun2spacy(token,hspell))

    def create_frame(self):
        sentence=self.sents[self.index]
        sent, pos, lemma = transpose(sentence[1])

        self.frame = ttk.Frame(self.root, height=800, padding=5, borderwidth=3, relief='raised')
        self.frame.pack(fill='both')

        button_sent = ttk.Button(self.frame, text=self.pretty_print(sentence[0]), command=self.EditSentence)
        button_sent.pack()

        self.tokens = []
        scrolled_frame = VerticalScrolledFrame(self.frame, height=700, width=700)
        scrolled_frame.pack()
        rt=[]
        for s, l, p in zip(sent, lemma, pos):
            frame_row = ttk.Frame(scrolled_frame.interior)
            frame_token = ttk.Frame(frame_row)
            frame_lemma = ttk.Frame(frame_row)
            frame_pos = ttk.Frame(frame_row)
            label = f'{len(self.tokens)}'
            while len(label) < 3:
                label = ' ' + label

            if self.warnings.get() and hspell and (color:=get_warning(hspell,s,l,p)):

                num_label = ttk.Label(frame_token, text=label, background=color)
            else:
                num_label = ttk.Label(frame_token, text=label)
            num_label.grid(column=0, row=0)

            pp_s = self.pretty_print(s,25)
            rt.append(s)
            s_button = ttk.Button(frame_token, text=pp_s, width=25, padding='we')#,command=lambda: self.EditToken(rt[len(self.tokens)]))

            s_button.grid(column=1, row=0)

            ll = tk.StringVar(frame_lemma)
            l_entry = ttk.Entry(frame_lemma, textvariable=ll, justify='center')
            l_entry.insert(tk.END, l)

            l_entry.pack()

            lp = tk.StringVar(frame_pos)
            lp.set(p)
            p_entry = ttk.Combobox(frame_pos, width=7, textvariable=lp)
            p_entry['values'] = postag
            p_entry['state'] = 'readonly'

            p_entry.grid(row=len(self.tokens), column=0)

            self.tokens.append((s, lp, ll))
            frame_token.grid(column=0, row=0)
            frame_lemma.grid(column=1, row=0)
            frame_pos.grid(column=2, row=0)
            frame_row.pack()


    def go_ahead(self,orientation):

        watchDog=0
        ok=False
        indx=self.index
        while watchDog<=len(self.sents) and not ok:
            watchDog+=1
            if indx == 0 and orientation<0:
                indx=len(self.sents)
            indx = (indx + orientation) % len(self.sents)

            sentence = self.sents[indx]
            token, pos, lemma = transpose(sentence[1])
            watch=[[t,l,p] for t,l,p in zip(token,lemma,pos)]
            watch=[item[self.radio.get()] for item in watch]
            ok=self.text_filter.get() in watch

        if ok:
            self.index=indx
        else:
            messagebox.showwarning(title='Warning',message=f'{self.text_filter.get()} no find')


    def index_down(self):

        #save current sentence
        self.sents[self.index] = (self.sents[self.index][0],
                                  tuple([(ll, lp.get(), lt.get()) for ll, lp, lt in self.tokens]))
        #go next sentence
        if self.filter.get():
            self.go_ahead(-1)
        else:
            self.index = self.index - 1 if self.index else len(self.sents) - 1
        self.index_sv.set(f'{self.index + 1}/{len(self.sents)}')
        self.frame.destroy()
        self.create_frame()

    def index_up(self):

        #save current sentence
        self.sents[self.index] = (self.sents[self.index][0],
                                  tuple([(ll, lp.get(), lt.get()) for ll, lp, lt in self.tokens]))

        #go next sentence
        if self.filter.get():
            self.go_ahead(1)
        else:
            self.index = (self.index + 1) % (len(self.sents))
        self.index_sv.set(f'{self.index + 1}/{len(self.sents)}')
        self.frame.destroy()
        self.create_frame()

    def goto_page(self):
        self.sents[self.index] = (self.sents[self.index][0],
                                  tuple([(ll.get(), lp.get(), lt.get()) for ll, lp, lt in self.tokens]))
        page = int(self.goto_sv.get()) - 1
        self.index = min(len(self.sents) - 1, max(0, page))
        self.index_sv.set(f'{self.index + 1}/{len(self.sents)}')
        self.frame.destroy()
        self.create_frame()

    def delete(self):
        self.frame.destroy()
        self.sents.pop(self.index)
        self.create_frame()
        self.index_sv.set(f'{self.index + 1}/{len(self.sents)}')

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':

    data_path = Path.cwd() / 'dataset/labeled_sents_10.pkl'
    
    model_path = Path.cwd() / 'Model'


    try:
        hspell = hunspell.HunSpell('/usr/share/hunspell/gl_ES.dic', '/usr/share/hunspell/gl_ES.aff')
    except:
        hspell=None
    corpus = pickle_var(model_path / 'wiki_gal_corpuscle.pkl')
    corpus.lang=spacy.load(model_path/'gl_lg')
    sents = pickle_var(data_path)



    window = WindowSentence(sentences=sents, corpus=corpus, data_path=data_path.parent)
