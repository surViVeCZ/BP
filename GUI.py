# -*- coding: utf-8 -*-
from base64 import encode
from cProfile import label
import sys
import tkinter as tk
from tkinter import LEFT, RIDGE, RIGHT, Button, Entry, filedialog, Text, Label
from tkinter import ttk
from tkinter import messagebox
import os
from tkinter.messagebox import showinfo

from matplotlib.pyplot import text
from steganography import main


## @brief zjistí zvolenou metodu v combo box
def method_changed(event):
    global method
    method = combo.current()
    
## @brief volba vstupního souboru
def choose_input():
    global text_path
    global filepath
    inputfile = filedialog.askopenfile(initialdir="/", title="Select file to encode",
    filetypes=(("documents", "*.docx"), ("text files", "*.txt")))
    if inputfile:
        filepath = os.path.abspath(inputfile.name)

    head_tail = os.path.split(filepath)
    text_path = Label(text = head_tail[1], background="#DCDFE0", foreground="#8B9092")
    text_path.place(x = 280, y = 90)
        
## @brief šifrování zvoleného souboru, zvolenou metodou a tajnou zprávou
def encode():
    global method
    method_name = ""
    secret_mes = message.get('1.0', 'end-1c')
    try:
        print('Message index is: {}\n'.format(method),  end = '')
    except:
        messagebox.showerror("Error", "You need to choose a method!")

    print("Secret message is: " + secret_mes)
    try:
        str(filepath)
    except:
        messagebox.showerror("Error", "You need to choose a cover file!")
    if method == 0:
        method_name = '-b'
    elif method == 1:
        method_name = '-w'
    elif method == 2:
        method_name = '-r'
    elif method == 3:
        method_name = '--own1'
    elif method == 4:
        method_name = '--own2'
    
    main(['-i', str(filepath), '-e', '-s', secret_mes, method_name])
    message.delete(1.0,"end")
    messagebox.showinfo("ENCODED!", "Zpráva byla úspěšně zašifrována do zvoleného souboru!")

## @brief dešifrování zvoleného souboru, zvolenou metodou
#@note soubor musí být dešifrován metodou, kterou byl zašifrován
def decode():
    global method
    global message
    method_name = ""
    try:
        print('Message index is: {}\n'.format(method),  end = '')
    except:
        messagebox.showerror("Error", "You need to choose a method!")
    try:
        str(filepath)
    except:
        messagebox.showerror("Error", "You need to choose a cover file!")
    if method == 0:
        method_name = '-b'
    elif method == 1:
        method_name = '-w'
    elif method == 2:
        method_name = '-r'
    elif method == 3:
        method_name = '--own1'
    elif method == 4:
        method_name = '--own2'

    secret = main(['-i', str(filepath), '-d', '-s', method_name])
    print(secret)
    message.delete(1.0,"end")
    message.insert('1.0', "secret")
    messagebox.showinfo("DECODED!", "Soubor byl dešifrován")

root = tk.Tk()
root.geometry("640x500")
root.maxsize(640,500)
root.minsize(640,500)
root.configure(background='#DCDFE0')
# Steganography tool for text encoding and decoding
heading = Label(text="STEGOSHARK 2000 ^^", bg="black", fg="white", height="3", width="800")
heading.pack()

l1 = Label(text = "Input file:", background="#DCDFE0")
l1.place(x = 20, y = 90)
#input file button
open_file = tk.Button(root, text = "Choose input file", padx=5,pady=5, bg="#4173EA", fg="#FFFFFF", 
            activebackground="#1C3A83", activeforeground="#FFFFFF", command=choose_input)
open_file.place(x = 120, y = 80)

l2 = Label(text = "Insert secret message you want to hide:", background="#DCDFE0")
l2.place(x = 20, y = 140)


#entry secret message
message = Text(root, bg="white", height="5", width="60")
message.place(x = 20, y = 170)

#encode button
encode_button = Button(root, text="ENCODE", command=encode, padx=85, bg="#4173EA", fg="#FFFFFF", activebackground="#1C3A83", activeforeground="#FFFFFF")
encode_button.place(x = 70, y = 450)

decode_button = Button(root, text="DECODE", command=decode, padx=85, bg="#4173EA", fg="#FFFFFF", activebackground="#1C3A83", activeforeground="#FFFFFF")
decode_button.place(x = 320, y = 450)


selected_method = tk.StringVar()
combo = ttk.Combobox(root,textvariable=selected_method, width=35)
combo['values'] = ["Baconova šifra", "Open-space metoda", "Metoda synonym", "Metoda synonym s baconovým šifrováním", "Huffmanovo kódování"]
combo['state'] = 'readonly'
combo.set('---')
combo.place(x = 20, y = 300)
combo.bind('<<ComboboxSelected>>', method_changed)

root.mainloop()