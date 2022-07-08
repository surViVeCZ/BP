#----------------------------------------------------------------------
# Autor:          Petr Pouč                                           
# Login:          xpoucp01
# Datum:          27.04.2022
# Název práce:    Digitální textová steganografie 
# Cíl práce:      Implementace 4 vybraných steganografických metod
#----------------------------------------------------------------------

from codecs import encode
import re
import os
import string
import sys
import timeit
import docx
import matplotlib.pyplot as plt
import numpy as np

#moduly
import bacon
import whitespaces
import xml_parse
import robustness
import synonyms
import steganography
from contextlib import contextmanager

## @brief celková velikost původních cover souborů
bacon_cover_size = 0
## @brief celková velikost zašifrovaných úspěšně zašifrovaných soborů Baconovým šifrováním
bacon_encoded_size = 0
## @brief celková velikost původních cover souborů
spaces_cover_size = 0
## @brief celková velikost zašifrovaných úspěšně zašifrovaných soborů Open-space metodou
spaces_encoded_size = 0
## @brief celková velikost původních cover souborů
syn_cover_size = 0
## @brief celková velikost zašifrovaných úspěšně zašifrovaných soborů metodou synonym
syn_encoded_size = 0

## @brief zpráva, která se během testů zašifruje do všech souborů
secret_message = "hromadnytest."
mes_len = len(secret_message)

## @brief zašifruje všechny soubory nacházející se ve složce cover_files
#@details každý soubor je šifrován každou steganografickou metodou 
#@note postupně jsou volány funkce encode_bacon(), encode_spaces(), encode_syn(), encode_own1(), encode_own2()
def encode_all_covers():
    encode_bacon()
    encode_spaces()
    encode_syn()
    encode_own1()
    encode_own2()


## @brief dešifruje všechny soubory nacházející se ve složce decodes
def decode_all_encodes():
    print("\n", end='')
    print("---------------------------------")
    print("DECODING:")
    decode_syn()
    decode_spaces()
    decode_bacon()

## @brief testy na robustnost pro 3 základní steganografické metody
#@note postupně jsou volány funkce bacon_robustness_check(), spaces_robustness_check(), syn_robustness_check()
def check_robustness(): 
    bacon_robustness_check()
    spaces_robustness_check()
    syn_robustness_check()

## @brief počítá o kolik % jsou zašifrované soubory vetší než původní
def calculate_SIR():
    bacon_sir = (bacon_encoded_size-bacon_cover_size)/bacon_cover_size*100
    spaces_sir = (spaces_encoded_size-spaces_cover_size)/spaces_cover_size*100
    syn_sir = (syn_encoded_size-syn_cover_size)/syn_cover_size*100
    print("BACON SIR:\t %f %%" % bacon_sir)
    print("SPACES SIR:\t %f %%" % spaces_sir)
    print("SYNONYMS SIR:\t %f %%" % syn_sir)

## @brief funkce vytváří grafy
#@note postupně jsou volány funkce plot_graphs1(), plot_graphs2(), plot_graphs3(),plot_graphs4()
def plot_all(): 
    plot_graphs1()
    plot_graphs2()
    plot_graphs3()
    plot_graphs4()

## @brief vytvoření koláčového grafu 
#@note graf představuje odpovědi lidí na otázku: "Přijde vám na některém z těhto souborů něco zvláštního?"
def plot_graphs1():

    #Přijde vám na některém z těhto souborů něco zvláštního?
    students = [1,2,2,4,4,10]
    cmap = plt.get_cmap('Greys')
    colors = list(cmap(np.linspace(0.45, 0.85, len(students))))
    # Swap in a bright blue for the Lacrosse color.
    colors[5] = 'dodgerblue'
    plt.rcParams.update({'font.size': 22})

    
    wierd = ['Open-space metoda', 'Open-space metoda a metoda synonym','Metoda synonym','Baconova šifra a metoda synonym', 'Baconova šifra', "Žádný ze zašifrovaných/Nezašifrovaný"]
    exp = [0.01,0.01,0.01,0.01,0.01,0.01]
    fig1 = plt.figure(figsize=(11, 9))
    patches, texts, autotexts = plt.pie(students, labels = wierd, explode = exp, autopct='%2.1f%%', colors=colors)
    texts[0].set_color('black')
    [autotext.set_color('white') for autotext in autotexts]

    plt.savefig("first.pdf",bbox_inches='tight')

## @brief vytvoření koláčového grafu 
#@note graf představuje odpovědi lidí na otázku: "Některý ze souborů je zašifrovaný, dokážete říci který?"
def plot_graphs2():
    #Některý ze souborů je zašifrovaný, dokážete říci který?
    students2 = [1,2,2,4,5,7,2]
    cmap = plt.get_cmap('Greys')
    colors2 = list(cmap(np.linspace(0.45, 0.85, len(students2))))
    plt.rcParams.update({'font.size': 22})

    # Swap in a bright blue for the Lacrosse color.
    colors2[5] = 'dodgerblue'
    not_changed = ['Open-space metoda', 'Open-space metoda a metoda synonym', 'Baconova šifra a Open-space metoda','Baconova šifra a metoda synonym', 'Metoda synonym', 'Baconova šifra','Všechny metody']
    exp2 = [0.01,0.01,0.01,0.01,0.01,0.01,0.01]
    fig2 = plt.figure(figsize=(11,9))
    patches2, texts2, autotexts2 = plt.pie(students2, labels = not_changed, explode = exp2, autopct='%2.1f%%', colors=colors2)
    texts2[0].set_color('black')
    [autotext2.set_color('white') for autotext2 in autotexts2]

    plt.savefig("second.pdf",bbox_inches='tight')
 

## @vypočítá maximální možnou velikost zprávy, kterou jde do určeného cover textu uložit
#@param file vstupní soubor
#@param method vybraná steganografická metoda
#@param file_format formát souboru (.docx/.txt)
#@return maximální počet znaků, který jsem schopen do textu ukrýt
def max_secret_message(file, method, file_format): 
    if file_format == "docx": 
        full_text = steganography.print_text(file)
    elif file_format == "txt":
        text_file = open(file)
        full_text = text_file.read()
 
    if method == "synonyms":
        words_available = synonyms.count_dictionary_words(full_text)/8
    elif method == "bacon" or method == "own1" or method == "own2":
        words_available = len(full_text.split())/5
    elif method == "spaces":
        words_available = len(full_text.split())/8

    return words_available


## @breaf při běhu testů vypne nechtěný výpis v konzoli (výpis u jednotlivých metod)
#@cite https://stackoverflow.com/questions/2125702/how-to-suppress-console-output-in-python
@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout

## @brief zjistí velikost složky
#@param full_path cesta ke složce
#@return velikost
def get_folder_size(full_path):
    size = 0
    for path, dirs, files in os.walk(full_path):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)
    return size


## @brief zašifruje všechny soubory nacházející se ve složce /cover_files/synonyms
#@details ve funkci dále počítám efektivitu,kapacitu a celkovou úspěšnost metody
def encode_syn():
    thisdir_bin = os.getcwdb()
    cover_size_path = os.getcwd() + '/cover_files/synonyms'
    path = bytes('/cover_files/synonyms', 'utf-8')

    changed_path = os.path.join(thisdir_bin, b"cover_files")
    changed_path = os.path.join(changed_path, b"synonyms")

    list_of_files = os.listdir(changed_path)

    cnt = 0
    message = 0
    success = 0
    global syn_cover_size
    print("\n", end='')
    print("REPLACING SYNONYMS ENCODING:")
    file_format = ""
    #šifrování všech cover textů pomocí metody synonym
    start = timeit.default_timer()
    for file in list_of_files:
        cnt += 1
        file = os.path.join(changed_path, file)    
        file = str(file, 'UTF-8')

        #zjistím si jméno souboru (poslední soubor v cestě)
        head_tail = os.path.split(file)
        file_name = head_tail[1]
        if file_name.endswith('.txt'):
            file_format = "txt"
        elif file_name.endswith('.docx'):
            file_format = "docx"

        message += max_secret_message(cover_size_path+'/'+file_name, "synonyms", file_format)
        with suppress_stdout():
            check = steganography.main(['-i', file, '-e', '-s', secret_message, '-r'])

        if check is False:
            print("#%d failed ✖ (%s)" % (cnt, file_name))
        else:
            print("#%d encoded 🗸 (%s)" % (cnt, file_name))
            size = os.stat(file)
            syn_cover_size += size.st_size
            success += 1    
    end = timeit.default_timer()
    time = (end - start)
    print("Elapsed time: \t\t%f \t[seconds] " % time)
    print("Cover texts size: \t%d \t[bytes]" % syn_cover_size)
    
    efficiency = time/(float(syn_cover_size)*0.001)
    success_rate = 100*(success/cnt)
    print("Efficiency: \t\t%f \t[time in seconds to encode 1KB]" % efficiency)
    capacity = float(message/syn_cover_size)*100.0
    print("Average capacity: \t%f \t[bits]" % (capacity))

    print("-------------------------------------------------------------------------")
    print("Success rate: \t\t %d/%d 〜 %g%%" % (success,cnt,success_rate))

## @brief zašifruje všechny soubory nacházející se ve složce /cover_files/synonyms
#@details ve funkci dále počítám efektivitu,kapacitu a celkovou úspěšnost metody
#@note při volání této funkce musím nastavit šifrování na --own1 (steganography.main(['-i', file, '-e', '-s', secret_message, '--own1']))
def encode_own1():
    thisdir_bin = os.getcwdb()
    cover_size_path = os.getcwd() + '/cover_files/synonyms'
    path = bytes('/cover_files/synonyms', 'utf-8')

    changed_path = os.path.join(thisdir_bin, b"cover_files")
    changed_path = os.path.join(changed_path, b"synonyms")

    list_of_files = os.listdir(changed_path)

    cnt = 0
    message = 0
    success = 0
    global syn_cover_size
    syn_cover_size = 0
    file_format = ""
    print("\n", end='')
    print("OWN1 ENCODING (SYN + BACON):")

    #šifrování všech cover textů pomocí metody synonym
    start = timeit.default_timer()
    for file in list_of_files:
        cnt += 1
        file = os.path.join(changed_path, file)    
        file = str(file, 'UTF-8')

        #zjistím si jméno souboru (poslední soubor v cestě)
        head_tail = os.path.split(file)
        file_name = head_tail[1]
        if file_name.endswith('.txt'):
            file_format = "txt"
        elif file_name.endswith('.docx'):
            file_format = "docx"

        message += max_secret_message(cover_size_path+'/'+file_name, "own1", file_format)
        with suppress_stdout():
            check = steganography.main(['-i', file, '-e', '-s', secret_message, '--own1'])

        if check is False:
            print("#%d failed ✖ (%s)" % (cnt, file_name))
        else:
            print("#%d encoded 🗸 (%s)" % (cnt, file_name))
            size = os.stat(file)
            syn_cover_size += size.st_size
            success += 1
    end = timeit.default_timer()
    time = (end - start)
    print("Elapsed time: \t\t%f \t[seconds] " % time)
    print("Cover texts size: \t%d \t[bytes]" % syn_cover_size)
    
    efficiency = time/(float(syn_cover_size)*0.001)
    success_rate = 100*(success/cnt)
    print("Efficiency: \t\t%f \t[time in seconds to encode 1KB]" % efficiency)
    capacity = float(message/syn_cover_size)*100.0
    print("Average capacity: \t%f \t[bits]" % (capacity))

    print("-------------------------------------------------------------------------")
    print("Success rate: \t\t %d/%d 〜 %g%%" % (success,cnt,success_rate))

## @brief zašifruje všechny soubory nacházející se ve složce /cover_files/synonyms
#@details ve funkci dále počítám efektivitu,kapacitu a celkovou úspěšnost metody
#@note při volání této funkce musím nastavit šifrování na --own2 (steganography.main(['-i', file, '-e', '-s', secret_message, '--own2']))
def encode_own2():
    thisdir_bin = os.getcwdb()
    cover_size_path = os.getcwd() + '/cover_files/synonyms'
    path = bytes('/cover_files/synonyms', 'utf-8')

    changed_path = os.path.join(thisdir_bin, b"cover_files")
    changed_path = os.path.join(changed_path, b"synonyms")

    list_of_files = os.listdir(changed_path)

    cnt = 0
    message = 0
    success = 0
    global syn_cover_size
    syn_cover_size = 0
    print("\n", end='')
    file_format = ""
    print("OWN2 ENCODING (SYN + HUFFMAN):")

    #šifrování všech cover textů pomocí metody synonym
    start = timeit.default_timer()
    for file in list_of_files:
        cnt += 1
        file = os.path.join(changed_path, file)    
        file = str(file, 'UTF-8')

        #zjistím si jméno souboru (poslední soubor v cestě)
        head_tail = os.path.split(file)
        file_name = head_tail[1]
        if file_name.endswith('.txt'):
            file_format = "txt"
        elif file_name.endswith('.docx'):
            file_format = "docx"

        message += max_secret_message(cover_size_path+'/'+file_name, "own2", file_format)
        with suppress_stdout():
            check = steganography.main(['-i', file, '-e', '-s', secret_message, '--own2'])

        if check is False:
            print("#%d failed ✖ (%s)" % (cnt, file_name))
        else:
            print("#%d encoded 🗸 (%s)" % (cnt, file_name))
            size = os.stat(file)
            syn_cover_size += size.st_size
            success += 1
    end = timeit.default_timer()
    time = (end - start)
    print("Elapsed time: \t\t%f \t[seconds] " % time)
    print("Cover texts size: \t%d \t[bytes]" % syn_cover_size)
    
    efficiency = time/(float(syn_cover_size)*0.001)
    success_rate = 100*(success/cnt)
    print("Efficiency: \t\t%f \t[time in seconds to encode 1KB]" % efficiency)
    capacity = float(message/syn_cover_size)*100.0
    print("Average capacity: \t%f \t[bits]" % (capacity))

    print("-------------------------------------------------------------------------")
    print("Success rate: \t\t %d/%d 〜 %g%%" % (success,cnt,success_rate))

## @brief zašifruje všechny soubory nacházející se ve složce /cover_files/spaces
#@details ve funkci dále počítám efektivitu,kapacitu a celkovou úspěšnost metody
def encode_spaces():
    thisdir_bin = os.getcwdb()
    cover_size_path = os.getcwd() + '/cover_files/spaces'
    path = bytes('/cover_files/spaces', 'utf-8')

    changed_path = os.path.join(thisdir_bin, b"cover_files")
    changed_path = os.path.join(changed_path, b"spaces")

    list_of_files = os.listdir(changed_path)

    cnt = 0
    success = 0
    global spaces_cover_size
    print("\n", end='')
    print("ADDING WHITESPACES ENCODING:")
    file_format = ""
     #šifrování všech cover textů pomocí vkládání mezislovních mezer
    message = 0
    start = timeit.default_timer()
    for file in list_of_files:
        cnt += 1
        file = os.path.join(changed_path, file)    
        file = str(file, 'UTF-8')

        #zjistím si jméno souboru (poslední soubor v cestě)
        head_tail = os.path.split(file)
        file_name = head_tail[1]
        if file_name.endswith('.txt'):
            file_format = "txt"
        elif file_name.endswith('.docx'):
            file_format = "docx"

        message += max_secret_message(cover_size_path+'/'+file_name, "spaces",file_format)
        with suppress_stdout():
            check = steganography.main(['-i', file, '-e', '-s', secret_message, '-w'])
        if check is False:
            print("#%d failed ✖ (%s)" % (cnt, file_name))
        else:
            print("#%d encoded 🗸 (%s)" % (cnt, file_name))
            size = os.stat(file)
            spaces_cover_size += size.st_size
            success += 1

    end = timeit.default_timer()
    time = (end - start)
    print("Elapsed time: \t\t%f \t[seconds] " % time)
    size = get_folder_size(cover_size_path)
    print("Cover texts size: \t%d \t[bytes]" % spaces_cover_size)
    
    efficiency = time/(float(spaces_cover_size)*0.001)
    success_rate = 100*(success/cnt)
    print("Efficiency: \t\t%f \t[time in seconds to encode 1KB]" % efficiency)
    capacity = float(message/spaces_cover_size)*100.0
    print("Average capacity: \t%f \t[bits]" % (capacity))
   
    print("-------------------------------------------------------------------------")
    print("Success rate: \t\t %d/%d 〜 %g%%" % (success,cnt,success_rate))

## @brief zašifruje všechny soubory nacházející se ve složce /cover_files/bacon
#@details ve funkci dále počítám efektivitu,kapacitu a celkovou úspěšnost metody
def encode_bacon():
    thisdir_bin = os.getcwdb()
    cover_size_path = os.getcwd() + '/cover_files/bacon'

    changed_path = os.path.join(thisdir_bin, b"cover_files")
    changed_path = os.path.join(changed_path, b"bacon")

    list_of_files = os.listdir(changed_path)

    cnt = 0
    message = 0
    success = 0
    global bacon_cover_size
    print("BACON ENCODING:")
    file_format = ""

    #šifrování všech cover textů pomocí Baconovy šifry
    start = timeit.default_timer()
    for file in list_of_files:
        cnt += 1
        file = os.path.join(changed_path, file)    
        file = str(file, 'UTF-8')
        #zjistím si jméno souboru (poslední soubor v cestě)
        head_tail = os.path.split(file)
        file_name = head_tail[1]
        if file_name.endswith('.txt'):
            file_format = "txt"
        elif file_name.endswith('.docx'):
            file_format = "docx"
    
        message += max_secret_message(cover_size_path+'/'+file_name, "bacon", file_format)
        with suppress_stdout():
            check = steganography.main(['-i', file, '-e', '-s', secret_message, '-b'])
     

        if check is False:
            print("#%d failed ✖ (%s)" % (cnt, file_name))
        else:
            print("#%d encoded 🗸 (%s)" % (cnt, file_name))
            size = os.stat(file)
            bacon_cover_size += size.st_size
            success += 1
    size = get_folder_size(cover_size_path)

    end = timeit.default_timer()
    time = (end - start)
    print("Elapsed time: \t\t%f \t[seconds] " % time)
    print("Cover texts size: \t%d \t[bytes]" % bacon_cover_size)
    
    efficiency = time/(float(bacon_cover_size)*0.001)
    success_rate = 100*(success/cnt)
    print("Efficiency: \t\t%f \t[time in seconds to encode 1KB]" % efficiency)
    capacity = float(message/bacon_cover_size)*100.0
    print("Average capacity: \t%f \t[bits]" % (capacity))
  
    print("-------------------------------------------------------------------------")
    print("Success rate: \t\t %d/%d 〜 %g%%" % (success,cnt,success_rate))

## @brief dešifruje všechny soubory nacházející se ve složce /encoded
#@details dešifruji pouze soubory zašifrované touto metodou - file.startswith("bacon")
#@note při šifrování metodou přidám k názvu souboru název steganografické metody (např. bacon_cover1.docx)
def decode_bacon():
    thisdir_bin = os.getcwdb()
    changed_path = os.path.join(thisdir_bin, b"encoded")

    list_of_files = os.listdir(changed_path)
    bacon_files = []
    encoded_path = os.getcwd()

    cnt = 0
    message = 0
    success = 0
    global bacon_encoded_size
    print("BACON DECODING:")
    for file in list_of_files:
        file = str(file, 'UTF-8')
     

        if file.startswith("bacon"):
            bacon_files.append(file)
            size = os.stat(encoded_path + "/encoded/" + file)
            bacon_encoded_size += size.st_size
       
    for encoded in bacon_files:
        robustness.change_font_style("encoded/" + encoded)
        cnt += 1
        with suppress_stdout():
            check = steganography.main(['-i', "encoded/" + encoded, '-d', '-s', '-b'])
            head_tail = os.path.split(encoded)
            file_name = head_tail[1]

    bacon_decodes = []
    decoded_path = os.path.join(thisdir_bin, b"decoded")
    list_of_decoded = os.listdir(decoded_path)

    #porovnání, jestli zpráva zůstala celá neporušená
    for file in list_of_decoded:
        file = str(file, 'UTF-8')
        if file.startswith("bacon"):
            bacon_decodes.append(file)

    cnt = 0
    success = 0
    failed = 0
    for decoded in bacon_decodes:
        cnt += 1
        text = steganography.print_text("decoded/"+decoded)
        text = text[0:mes_len]
        #zpráva zůstala zachována
        if text.lower() == secret_message.lower():
            success += 1
        else:
            failed += 1

    #úspěšně se zachovaly všechny zprávy
    if failed == 0:
        print("All messages DECODED SUCCESSFULLY!")
        print("\n", end='')
    else:
        print("DECODED %d/%d" % (success,cnt))
        print("\n", end='')

## @brief dešifruje všechny soubory nacházející se ve složce /encoded
#@details dešifruji pouze soubory zašifrované touto metodou - file.startswith("spaces")
#@note při šifrování metodou přidám k názvu souboru název steganografické metody (např. spaces_cover1.docx)
def decode_spaces():
    thisdir_bin = os.getcwdb()
    changed_path = os.path.join(thisdir_bin, b"encoded")

    list_of_files = os.listdir(changed_path)
    spaces_files = []
    encoded_path = os.getcwd()

    cnt = 0
    message = 0
    success = 0
    global spaces_encoded_size
    print("SPACES DECODING:")
    for file in list_of_files:
        file = str(file, 'UTF-8')
     

        if file.startswith("spaces"):
            spaces_files.append(file)
            size = os.stat(encoded_path + "/encoded/" + file)
            spaces_encoded_size += size.st_size
       
    for encoded in spaces_files:
        with suppress_stdout():
            check = steganography.main(['-i', "encoded/" + encoded, '-d', '-s', '-w'])
            head_tail = os.path.split(encoded)
            file_name = head_tail[1]
            

    spaces_decodes = []
    decoded_path = os.path.join(thisdir_bin, b"decoded")
    list_of_decoded = os.listdir(decoded_path)

    #porovnání, jestli zpráva zůstala celá neporušená
    for file in list_of_decoded:
        file = str(file, 'UTF-8')
        if file.startswith("spaces"):
            spaces_decodes.append(file)

    cnt = 0
    success = 0
    failed = 0
    for decoded in spaces_decodes:
        cnt += 1
        text = steganography.print_text("decoded/"+decoded)
        text = text[0:mes_len]

        #zpráva zůstala zachována
        if text.lower() == secret_message.lower():
            success += 1
        else:
            failed += 1

    #úspěšně se zachovaly všechny zprávy
    if failed == 0:
        print("All messages DECODED SUCCESSFULLY!")
        print("\n", end='')
    else:
        print("DECODED %d/%d" % (success,cnt))
        print("\n", end='')


## @brief dešifruje všechny soubory nacházející se ve složce /encoded
#@details dešifruji pouze soubory zašifrované touto metodou - file.startswith("synonyms")
#@note při šifrování metodou přidám k názvu souboru název steganografické metody (např. synonyms_cover1.docx)
def decode_syn():
    thisdir_bin = os.getcwdb()
    changed_path = os.path.join(thisdir_bin, b"encoded")

    list_of_files = os.listdir(changed_path)
    syn_files = []
    encoded_path = os.getcwd()

    cnt = 0
    message = 0
    success = 0
    global syn_encoded_size
    print("SYNONYMS DECODING:")
    for file in list_of_files:
        file = str(file, 'UTF-8')
     

        if file.startswith("synonyms"):
            syn_files.append(file)
            size = os.stat(encoded_path + "/encoded/" + file)
            syn_encoded_size += size.st_size
       
    for encoded in syn_files:
        with suppress_stdout():
            check = steganography.main(['-i', "encoded/" + encoded, '-d', '-s', '-r'])
            head_tail = os.path.split(encoded)
            file_name = head_tail[1]
            
        # if check is False:
        #     print("#%d failed ✖ (%s)" % (cnt, file_name))
        # else:
        #     print("#%d decoded 🗸 (%s)" % (cnt, file_name))

    syn_decodes = []
    decoded_path = os.path.join(thisdir_bin, b"decoded")
    list_of_decoded = os.listdir(decoded_path)

    # #porovnání, jestli zpráva zůstala celá neporušená
    for file in list_of_decoded:
        file = str(file, 'UTF-8')
        if file.startswith("synonyms"):
            syn_decodes.append(file)

    cnt = 0
    success = 0
    failed = 0
    for decoded in syn_decodes:
        cnt += 1
        text = steganography.print_text("decoded/"+decoded)
        text = text[0:mes_len]

        #zpráva zůstala zachována
        if text.lower() == secret_message.lower():
            success += 1
        else:
            failed += 1

    #úspěšně se zachovaly všechny zprávy
    if failed == 0:
        print("All messages DECODED SUCCESSFULLY!")
        print("\n", end='')
    else:
        print("DECODED %d/%d" % (success,cnt))
        print("\n", end='')

## @brief "baconovým" souborům (file.startswith("bacon") ve složce /encoded postupně pomocí funkce change_font_style() měním formátování
#@details soubory se změněným formátováním se uloží do složky /robustness kterou následně dešifruji a kontroluji, zda-li zůstala tajná zpráva zachována
def bacon_robustness_check():
    thisdir_bin = os.getcwdb()
    changed_path = os.path.join(thisdir_bin, b"encoded")
    robustness_path = os.path.join(thisdir_bin, b"robustness")

    list_of_files = os.listdir(changed_path)
    bacon_changed_files = []
    bacon_files = []
 

    print("BACON ROBBUSTNESS CHECK:")
    for file in list_of_files:
        file = str(file, 'UTF-8')
     
        if file.startswith("bacon"):
            bacon_files.append(file)
    #změna formátování
    for encoded in bacon_files:
        robustness.change_font_style("encoded/" + encoded)

    list_of_changed_styles = os.listdir(robustness_path)
    

    #vyberu pouze souboru pro tuto metodu
    for changed in list_of_changed_styles:
        file = str(changed, 'UTF-8')
        if file.startswith("bacon"):
            bacon_changed_files.append(file)

    decoded_path = os.path.join(thisdir_bin, b"decoded")

    cnt = 0
    success = 0
    failed = 0
    for bacon_changed in bacon_changed_files:
        cnt += 1
        with suppress_stdout():
            #dekodování souboru se změněným stylem
            steganography.main(['-i', "robustness/" + bacon_changed, '-d', '-s', '-b'])
            text = steganography.print_text("robustness/"+ bacon_changed)

        #ořezání zprávy
        text = text[0:mes_len]
        #zpráva zůstala zachována
        if text.lower() == secret_message.lower():
            success += 1
        else:
            failed += 1

    #úspěšně se zachovaly všechny zprávy
    if failed == 0:
        print("After ALL FORMAT CHANGES all messages DECODED SUCCESSFULLY!")
        print("\n", end='')
    else:
        print("After ALL FORMAT CHANGES %d/%d messages sucesfully decoded" % (success,cnt))
        print("\n", end='')



## @brief "open-space" souborům (file.startswith("spaces") ve složce /encoded postupně pomocí funkce change_font_style() měním formátování
#@details soubory se změněným formátováním se uloží do složky /robustness kterou následně dešifruji a kontroluji, zda-li zůstala tajná zpráva zachována
def spaces_robustness_check():
    thisdir_bin = os.getcwdb()
    changed_path = os.path.join(thisdir_bin, b"encoded")
    robustness_path = os.path.join(thisdir_bin, b"robustness")

    list_of_files = os.listdir(changed_path)
    spaces_changed_files = []
    spaces_files = []
 

    print("OPEN-SPACE ROBBUSTNESS CHECK:")
    for file in list_of_files:
        file = str(file, 'UTF-8')
     
        if file.startswith("spaces"):
            spaces_files.append(file)
    #změna formátování
    for encoded in spaces_files:
        robustness.change_font_style("encoded/" + encoded)

    list_of_changed_styles = os.listdir(robustness_path)
    

    #vyberu pouze souboru pro tuto metodu
    for changed in list_of_changed_styles:
        file = str(changed, 'UTF-8')
        if file.startswith("spaces"):
            spaces_changed_files.append(file)

    decoded_path = os.path.join(thisdir_bin, b"decoded")

    cnt = 0
    success = 0
    failed = 0
    for spaces_changed in spaces_changed_files:
        cnt += 1
        with suppress_stdout():
            #dekodování souboru se změněným stylem
            steganography.main(['-i', "robustness/" + spaces_changed, '-d', '-s', '-w'])
            text = steganography.print_text("robustness/"+ spaces_changed)

        #ořezání zprávy
        text = text[0:mes_len]
        #zpráva zůstala zachována
        if text.lower() == secret_message.lower():
            success += 1
        else:
            failed += 1

    #úspěšně se zachovaly všechny zprávy
    if failed == 0:
        print("After ALL FORMAT CHANGES all messages DECODED SUCCESSFULLY!")
        print("\n", end='')
    else:
        print("After ALL FORMAT CHANGES %d/%d messages sucesfully decoded" % (success,cnt))
        print("\n", end='')

## @brief "synonyms" souborům (file.startswith("synonyms") ve složce /encoded postupně pomocí funkce change_font_style() měním formátování
#@details soubory se změněným formátováním se uloží do složky /robustness kterou následně dešifruji a kontroluji, zda-li zůstala tajná zpráva zachována
def syn_robustness_check():
    thisdir_bin = os.getcwdb()
    changed_path = os.path.join(thisdir_bin, b"encoded")
    robustness_path = os.path.join(thisdir_bin, b"robustness")

    list_of_files = os.listdir(changed_path)
    syn_changed_files = []
    syn_files = []
 

    print("SYNONYMS ROBBUSTNESS CHECK:")
    for file in list_of_files:
        file = str(file, 'UTF-8')
     
        if file.startswith("syn"):
            syn_files.append(file)
    #změna formátování
    for encoded in syn_files:
        robustness.change_font_style("encoded/" + encoded)

    list_of_changed_styles = os.listdir(robustness_path)
    

    #vyberu pouze souboru pro tuto metodu
    for changed in list_of_changed_styles:
        file = str(changed, 'UTF-8')
        if file.startswith("syn"):
            syn_changed_files.append(file)

    decoded_path = os.path.join(thisdir_bin, b"decoded")

    cnt = 0
    success = 0
    failed = 0
    for syn_chnaged in syn_changed_files:
        cnt += 1
        with suppress_stdout():
            #dekodování souboru se změněným stylem
            steganography.main(['-i', "robustness/" + syn_chnaged, '-d', '-s', '-r'])
            text = steganography.print_text("robustness/"+ syn_chnaged)

        #ořezání zprávy
        text = text[0:mes_len]
        #zpráva zůstala zachována
        if text.lower() == secret_message.lower():
            success += 1
        else:
            failed += 1

    #úspěšně se zachovaly všechny zprávy
    if failed == 0:
        print("After ALL FORMAT CHANGES all messages DECODED SUCCESSFULLY!")
        print("\n", end='')
    else:
        print("After ALL FORMAT CHANGES %d/%d messages sucesfully decoded" % (success,cnt))
        print("\n", end='')

## @brief vytvoření grafu
#@note graf představuje porovnání efektivity 3 základních steganografických metod 
def plot_graphs3():
    #metoda synonym
    y = [0.0065,0.023,0.017,0.021]
    x = [12,40,80,120]

    #baconova šifra
    y2 = [0.005,0.021,0.018,0.026]

    #open-space
    y3 = [0.007,0.036,0.032,0.035]
    fig3 = plt.figure(figsize=(11,9))

    plt.plot(x,y)
    plt.plot(x,y2)
    plt.plot(x,y3)
    plt.title("Efektivita jednotlivých metod")
    plt.ylabel("Čas potřebný k zašifrování 1kB dat [s]")
    plt.xlabel("Velikost cover souboru [kB]")

    ax = plt.gca()
    ax.legend(['Metoda synonym', 'Baconova šifra', 'Ope-space'])

    plt.savefig("effectivness.pdf",bbox_inches='tight')

## @brief vytvoření grafu
#@note graf představuje porovnání metody synonym a mých 2 upravených metod
#@note cílem modifikací bylo zvýšení kapacity, jak je z grafu vidět, tato modifikace neměla vliv na výkon metody
def plot_graphs4():
    #metoda synonym
    y = [0.0065,0.023,0.017,0.021]
    x = [12,40,80,120]

    #baconova šifra
    y2 = [0.012,0.022,0.018,0.022]

    #open-space
    y3 = [0.009,0.02,0.019,0.023]
    fig4 = plt.figure(figsize=(11,9))

    plt.plot(x,y)
    plt.plot(x,y2)
    plt.plot(x,y3)
    plt.title("Efektivita jednotlivých metod")
    plt.ylabel("Čas potřebný k zašifrování 1kB dat [s]")
    plt.xlabel("Velikost cover souboru [kB]")

    ax = plt.gca()
    ax.legend(['Metoda synonym', 'Metoda synonym + Baconovo šifrování', 'Metoda synonym + Huffmanovo kódování'])

    plt.savefig("own_methods_comparison.pdf",bbox_inches='tight')


if __name__ == "__main__":
    # šifrování všech souborů ve složce cover_files
    encode_all_covers()
    #dešifrování a kontrola, zda zůstala zachována tajná zpráva
    decode_all_encodes()
    #změna formátování a kontrola změny tajné zprávy
    check_robustness()
    # #výpočet změny velikosti souborů po vložení tajné zprávy
    calculate_SIR()
    # vykreslení grafů 
    plot_all()