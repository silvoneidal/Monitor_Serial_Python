# pyinstaller --onefile -w seu_script.py

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import serial
import threading
import serial.tools.list_ports

# Variável global para controlar a conexão serial
ser = None
is_connected = False
new_fonte = ("Courier New", 10)

# Função para listar portas COM ativas
def listar_portas():
    return [port.device for port in serial.tools.list_ports.comports()]

# Função para atualizar a combobox com as portas disponíveis
def atualizar_com_port_combo():
    com_port_combo.set('')  # Limpa o texto selecionado da combobox
    portas = listar_portas()
    com_port_combo['values'] = portas  # Atualiza os valores da combobox
    if portas:
        com_port_combo.current(0)  # Seleciona a primeira porta, se houver
                    
# Função para leitura da porta serial
def read_serial():
    while ser and ser.is_open:
        try:
            data = ser.readline().decode('utf-8').strip()
            if data:
                text_area.insert(tk.END, data + '\n')
                text_area.yview(tk.END)  # Scroll automático para o fim
        except Exception as e:
            if ser:
                ser.close()
            is_connected = False
            connect_button.config(text="Conectar")  # Muda o botão de volta para "Conectar"
            scan_button.config(state='normal')  # Habilita o botão
            com_port_combo.config(state='normal')  # Habilita o combo
            baudrate_combo.config(state='normal')  # Habilita o combo
            conectar_serial() # Somente para atualizar variáveis
            atualizar_com_port_combo() # Atualizar portas ativas
            print(f"Erro ao ler da porta serial: {e}")
            print(f"Porta desconectada...")


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
            entry.delete(0, tk.END)
    except Exception as e:
        print(f"Erro ao enviar dados: {e}")

# Função para conectar/desconectar à porta serial
def conectar_serial():
    global ser, is_connected

    if not is_connected:
        try:
            # Conectar à porta serial
            com_port = com_port_combo.get()
            baudrate = baudrate_combo.get()
            ser = serial.Serial(com_port, baudrate=int(baudrate), timeout=1)
            is_connected = True
            connect_button.config(text="Desconectar")  # Muda o botão para "Desconectar"
            scan_button.config(state='disabled')  # Desabilita o botão
            com_port_combo.config(state='disabled')  # Desabilita o combo
            baudrate_combo.config(state='disabled')  # Desabilita o combo
            
            # Iniciar a leitura da porta serial em uma thread separada
            thread = threading.Thread(target=read_serial)
            thread.daemon = True
            thread.start()

        except serial.SerialException as e:
            print(f"Erro ao conectar à porta serial: {e}")
    else:
        try:
            # Desconectar da porta serial
            if ser:
                ser.close()
            is_connected = False
            connect_button.config(text="Conectar")  # Muda o botão de volta para "Conectar"
            scan_button.config(state='normal')  # Habilita o botão
            com_port_combo.config(state='normal')  # Habilita o combo
            baudrate_combo.config(state='normal')  # Habilita o combo
        except Exception as e:
            print(f"Erro ao desconectar: {e}")

# Interface Tkinter
root = tk.Tk()
root.title("Monitor Serial Python by DALÇÓQUIO AUTOMAÇÃO")
root.geometry("1200x800")

# Frame para configurações
frame_config = tk.Frame(root)
frame_config.pack(pady=10)

# ComboBox para portas COM
try:
    com_label = tk.Label(frame_config, font=new_fonte, text="Porta COM:")
    com_label.grid(row=0, column=0, padx=3)
    com_port_combo = ttk.Combobox(frame_config, font=new_fonte, values=listar_portas(), width=10,  state="readonly")
    com_port_combo.grid(row=0, column=1, padx=3)
    com_port_combo.current(0)  # Seleciona a primeira porta
except Exception as e:
    print(f"Erro ao localizar portas disponíveis !!!")

# Atualiza as portas COM no combo após criar a combobox
atualizar_com_port_combo()

# ComboBox para baudrate
baudrate_label = tk.Label(frame_config, font=new_fonte, text="Baudrate:")
baudrate_label.grid(row=0, column=2, padx=3, pady=5)
baudrate_combo = ttk.Combobox(frame_config, font=new_fonte, values=["1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200"], width=10, state="readonly")
baudrate_combo.grid(row=0, column=3, padx=3, pady=5)
baudrate_combo.current(3)  # Seleciona 9600 por padrão

# Botão para conectar/desconectar
connect_button = tk.Button(frame_config, font=new_fonte, text="Conectar", command=conectar_serial, width=15)
connect_button.grid(row=0, column=4, padx=30, pady=10)

# Botão para scanear portas
scan_button = tk.Button(frame_config, font=new_fonte, text="Scanear", command=atualizar_com_port_combo, width=15)
scan_button.grid(row=0, column=5, padx=0, pady=10)

# Área de texto para exibir dados recebidos
text_area = scrolledtext.ScrolledText(root, font=new_fonte, width=145, height=40)
text_area.pack()

# Frame para entrada e envio de dados
frame_entry = tk.Frame(root)
frame_entry.pack(pady=10)

# Entrada de texto para enviar dados
entry = tk.Entry(frame_entry, font=new_fonte, width=110)
entry.grid(row=0, column=0, padx=3, pady=10)

# Caracter para fim de linha
endline_combo = ttk.Combobox(frame_entry, font=new_fonte, values=["None", "New Line", "Carriage Return", "Both NL and CR"], width=15, state="readonly")
endline_combo.grid(row=0, column=2, padx=3, pady=10)
endline_combo.current(0)  # Seleciona None por padrão

# Botão para enviar dados
send_button = tk.Button(frame_entry, font=new_fonte, text="Enviar", command=send_data, width=15)
send_button.grid(row=0, column=3, padx=10, pady=10)

# Enter para enviar dados
entry.bind('<Return>', lambda event: send_data())

print(messagebox.showinfo(title="Versão", message="Firmware v1.0!"))

root.mainloop()

# Fechar a porta serial ao encerrar o programa
if ser and ser.is_open:
    ser.close()
