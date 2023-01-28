from Galutils import *
from spacy import displacy

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM


import tkinter as tk
from tkinter import filedialog

import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *

from PIL import ImageTk,Image


class DiagramWindow():
    def __init__(self,image):

        self.diagWin=ttk.Toplevel()

        self.control_frame=ttk.Frame(self.diagWin, padding=3, borderwidth=3,relief='raised')
        self.control_frame.pack()
        self.save_button=ttk.Button(self.control_frame,text='Gardar imaxe',command=lambda: self.SaveImage(image))
        self.save_button.pack(side=LEFT, padx=3, pady=3)
        self.exit_button=ttk.Button(self.control_frame,text='Sair',command=lambda: self.diagWin.destroy())
        self.exit_button.pack(side=LEFT, padx=3, pady=3)

        self.diag_frame = ttk.Frame(self.diagWin, padding=3, borderwidth=3, relief='raised')

        self.scrollbar=tk.Scrollbar(self.diag_frame, orient=HORIZONTAL)
        self.scrollbar.pack(side="bottom", fill="x")

        image=Image.open(image)
        width, height  = image.size
        scale=1#min(1200/width,800/height)
        img=image.resize((int(width*scale),int(height*scale)),resample=0)
        self.bg = ImageTk.PhotoImage(img)

        self.canvas = ttk.Canvas(self.diag_frame, background="#fff",
                                 height=height*scale, width=width*scale,)


        self.canvas.create_image((0, 0), image=self.bg, anchor="nw")
        self.canvas.image=self.bg
        self.canvas.update()
        self.canvas.pack(fill='both', expand=True)
        self.diag_frame.pack(fill=BOTH, expand=YES)
        self.scrollbar.config(command=self.canvas.xview)
        self.canvas.config(scrollregion=((0,0,width,height)))
        self.canvas['xscrollcommand']=self.scrollbar.set#(0.49,.51)

        self.diagWin.mainloop()

    def SaveImage(self,image):
        name=filedialog.asksaveasfilename(title='Gardar imaxe...',
                                          filetypes = (('png files','*.png'),
                                                       ("jpeg files","*.jpg"),
                                                       ("all files","*.*")))
        if name:
            image.save(name)

class Main_Window:
    def __init__(self):
        self.root = tk.Tk()
        style = ttk.Style("darkly")

        text_frame = ttk.Frame(self.root, padding=5, borderwidth=5, relief='raised')
        text_frame.pack()
        text_label = ttk.Label(text_frame, text='Texto')
        text_label.pack()

        self.text_Text = ttk.Text(self.root, width=80, height=10, wrap='word', bg='blue')
        self.text_Text.pack()

        control_frame = ttk.Frame(self.root)
        control_frame.pack()

        self.an_button = ttk.Button(control_frame, text='Análise',
                               command=lambda: self.analisis_sent(self.text_Text.get('1.0', 'end'), corpus))
        self.an_button.pack(side=LEFT, padx=3, pady=3)

        diag_button=ttk.Button(control_frame,text='Diagrama',command=lambda: self.diagram_frame(self.text_Text.get('1.0', 'end'), corpus))
        diag_button.pack(side=LEFT, padx=3, pady=3)

        clean_button = ttk.Button(control_frame, text='Limpar', command=lambda: self.clean_analisis())
        clean_button.pack(side=LEFT, padx=3, pady=3)

        exit_button = ttk.Button(control_frame, text='Sair', command=lambda: self.root.destroy())
        exit_button.pack(side=LEFT, padx=3, pady=3)
        self.tok_frame=None
        self.diag_frame=None
        self.root.mainloop()


    def analisis_sent(self,sent,corpus):
        sent=sent.replace('\n',' ')
        #print(corpus.model_predict(sent))
        doc=corpus.lang(sent)
        if self.tok_frame:
            self.tok_frame.destroy()
            self.tok_frame=None
        self.tok_frame = ttk.Frame(self.root,padding=3,borderwidth=3,relief='raised')
        self.tok_frame.pack()
        values=[(token.text,token.lemma_,token.pos_,token.dep_,token.morph) for token in doc]

        tok_tree = Tableview(self.tok_frame, coldata=['token', 'lemma', 'POS','dep','morph'], rowdata=values,
                             autofit=True,height=min(15,len(values)))
        tok_tree.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        values = [(chunk.text, chunk.root.text,chunk.root.dep_,chunk.root.head.text) for chunk in doc.noun_chunks]
        if values:
            noun_label=ttk.Label(self.tok_frame,text='Anacos nominais (Text chunks)')
            noun_label.pack()
            noun_tree=Tableview(self.tok_frame,coldata=['texto','raíz','dep raíz','antecesor'],
                                rowdata=values,autofit=True,height=min(10,len(values)))
            noun_tree.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        values=[(e.text,e.label_) for e in doc.ents]
        if values:
            ent_label=ttk.Label(self.tok_frame,text='Entidades recoñecidas:')
            ent_label.pack()
            for text,label in values:
                val_label=ttk.Label(self.tok_frame,text=f'{text}-->{label}')
                val_label.pack()



    def diagram_frame(self,sentence,corpus):
        sentence=sentence.replace('\n',' ').strip()
        doc=corpus.lang(sentence)
        svg=displacy.render(doc, style="dep", jupyter=False)
        svg_path=Path.cwd()/'image.svg'
        png_path=Path.cwd()/'image.png'
        svg_path.open("w", encoding="utf-8").write(svg)
        drawing = svg2rlg(svg_path)

        renderPM.drawToFile(drawing, png_path, fmt='PNG')

        DiagramWindow(str(png_path))


    def clean_analisis(self):
        if self.tok_frame:
            self.tok_frame.destroy()
            self.tok_frame=None

        self.text_Text.delete('1.0','end')


model_path = Path.cwd()/'Model'
corpus = pickle_var(model_path / 'wiki_gal_corpuscle.pkl')
corpus.set_lang(model_path/'gl_lg')
Main_Window()
