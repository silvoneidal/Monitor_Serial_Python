 # pyinstaller --onefile -w seu_script.py

import tkinter as tk
from tkinter import ttk, scrolledtext, Text
import customtkinter as ctk
import serial
import threading
import serial.tools.list_ports
import time

# Configurando o tema da janela
ctk.set_appearance_mode("dark")  # Pode ser "light", "dark", ou "system" (baseado no SO)
ctk.set_default_color_theme("dark-blue")  # Pode ajustar o tema de cor também, blue, dark-blue, green

# Variável global para controlar a conexão serial
ser = None
is_connected = False
new_fonte = ("Courier New", 12)

# Função para listar portas COM ativas
def listar_portas():
    return [port.device for port in serial.tools.list_ports.comports()]

# Função para atualizar a combobox com as portas disponíveis
def atualizar_com_port_combo():
    com_port_combo.set('')  # Limpa o texto selecionado da combobox
    portas = listar_portas()
    com_port_combo.configure(values=portas)  # Atualiza os valores da combobox
    if portas:
        com_port_combo.set(portas[0])  # Seleciona a primeira porta, se houver
                    
# Função para leitura da porta serial
def read_serial():
    global is_connected
    while ser and ser.is_open:
        try:
            data = ser.readline().decode('utf-8').strip()
            if data:
                text_area.insert("end", data + '\n')
                text_area.yview("end")  # Scroll automático para o fim
        except Exception as e:
            if e.args[0] == f"GetOverlappedResult failed (PermissionError(13, 'Acesso negado.', None, 5))":
                ser.close()
                is_connected = False
                connect_button.configure(text="Conectar")  # Muda o botão de volta para "Conectar"
                scan_button.configure(state='normal')  # Habilita o botão
                com_port_combo.configure(state='normal')  # Habilita o combo
                baudrate_combo.configure(state='normal')  # Habilita o combo
                conectar_serial() # Somente para atualizar variáveis
                atualizar_com_port_combo() # Atualizar portas ativas
                print(f"Porta desconectada...")
            print(f"Erro ao ler da porta serial: {e}")
            

# Função para enviar dados
def send_data():
    data = entry.get()
    try:
        if ser and ser.is_open:
            if endline_combo.get() == "None":
                ser.write(data.encode('utf-8'))
            elif endline_combo.get() == "New Line":
                ser.write(data.encode('utf-8') + b'\n')
            elif endline_combo.get() == "Carriage Return":
                ser.write(data.encode('utf-8') + b'\r')
            elif endline_combo.get() == "Both NL and CR":
                ser.write(data.encode('utf-8') + b'\n\r')
            entry.delete(0, "end")
    except Exception as e:
        print(f"Erro ao enviar dados: {e}")

# Função para conectar/desconectar à porta serial
def conectar_serial():
    global ser, is_connected

    if not is_connected:
        try:
            com_port = com_port_combo.get()
            baudrate = baudrate_combo.get()
            ser = serial.Serial(com_port, baudrate=int(baudrate), timeout=1)
            is_connected = True
            connect_button.configure(text="Desconectar")
            scan_button.configure(state='disabled')
            com_port_combo.configure(state='disabled')
            baudrate_combo.configure(state='disabled')
            style.configure("TLabel", background="blue")
            frame_conexao.configure(style="TLabel")
            
            # Iniciar a leitura da porta serial em uma thread separada
            thread = threading.Thread(target=read_serial)
            thread.daemon = True
            thread.start()

        except serial.SerialException as e:
            print(f"Erro ao conectar à porta serial: {e}")
    else:
        try:
            if ser:
                ser.close()
                is_connected = False
                connect_button.configure(text="Conectar")
                scan_button.configure(state='normal')
                com_port_combo.configure(state='normal')
                baudrate_combo.configure(state='normal')
                style.configure("TLabel", background="red")
                frame_conexao.configure(style="TLabel")
        except Exception as e:
            print(f"Erro ao desconectar: {e}")

# Função para sinalizar dados recebidos pela serial
def show_received_message():
    style.configure("TLabel", background="yellow")
    frame_conexao.configure(style="TLabel")
    root.after(500, clear_received_message) # Mostra por 500ms (0.5 segundos)

def clear_received_message():
    style.configure("TLabel", background="blue")
    frame_conexao.configure(style="TLabel")

    
# Interface CustomTkinter
root = ctk.CTk()
root.title("Monitor Serial Python by DALÇÓQUIO AUTOMAÇÃO")
root.geometry("600x300")

# Frame para configurações
frame_config = ctk.CTkFrame(root, height=50)
frame_config.grid(row=0, column=0, sticky="ew", padx=0, pady=10) # Usando grid 
frame_config.grid_propagate(False)

# ComboBox para portas COM
com_port_combo = ctk.CTkComboBox(frame_config, font=new_fonte, values=listar_portas(), width=124, state="readonly")
com_port_combo.pack(side=tk.LEFT, padx=10)

# Atualiza as portas COM no combo após criar a combobox
atualizar_com_port_combo()

# ComboBox para baudrate
baudrate_combo = ctk.CTkComboBox(frame_config, font=new_fonte, values=["1200", "2400", "4800", "9600",  "19200", "38400", "57600", "115200"], width=124, state="readonly")
baudrate_combo.pack(side=tk.LEFT, padx=0)
baudrate_combo.set("9600")  # Seleciona 9600 por padrão

# Botão para scanear portas
scan_button = ctk.CTkButton(frame_config, font=new_fonte, text="Scanear", command=atualizar_com_port_combo, width=150)
scan_button.pack(side=tk.LEFT, padx=10)

# Botão para conectar/desconectar
connect_button = ctk.CTkButton(frame_config, font=new_fonte, text="Conectar", command=conectar_serial, width=150)
connect_button.pack(side=tk.LEFT, padx=0)

# Frame para dados recebidos
frame_area = ctk.CTkFrame(root)
frame_area.grid(row=1, column=0, sticky="nsew", padx=0, pady=0) # Usando grid
root.columnconfigure(0, weight=1) # Faz a coluna se expandir para ocupar todo o espaço
root.rowconfigure(1, weight=1)    # Faz a linha se expandir para ocupar todo o espaço

# Área de texto para exibir dados recebidos ( com custom tkinter)
#text_area = ctk.CTkTextbox(frame_area, font=new_fonte, width=1000, height=450)
#text_area.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

# Área de texto para exibir dados recebidos ( com tkinter)
text_area = Text(frame_area, width=145, height=40) 
text_area.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

# Frame para entrada e envio de dados
frame_entry = ctk.CTkFrame(root, width=1000, height=50)
frame_entry.grid(row=2, column=0, sticky="nsew", padx=0, pady=10) # Usando grid

# Entrada de texto para enviar dados
entry = ctk.CTkEntry(frame_entry, font=new_fonte, width=420)
entry.pack(side=tk.LEFT, padx=10)

# Combobox para caracter para fim de linha
endline_combo = ctk.CTkComboBox(frame_entry, font=new_fonte, values=["None", "New Line", "Carriage Return", "Both NL and CR"], width=150, state="readonly")
endline_combo.pack(side=tk.LEFT, padx=0)
endline_combo.set("None")

# Enter para enviar dados
entry.bind('<Return>', lambda event: send_data())

# Frame para sinalizar conexão serial
style = ttk.Style()
style.configure("TLabel", background="red") # Definindo o estilo para Desconectado 
frame_conexao = ttk.Frame(root, width=500, height=10, style="TLabel")
frame_conexao.grid(row=3, column=0, sticky="ew") # Usando grid aqui também


root.mainloop()

# Fechar a porta serial ao encerrar o programa
if ser and ser.is_open:
    ser.close()
