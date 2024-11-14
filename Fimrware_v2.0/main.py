 # pyinstaller --onefile -w seu_script.py

import customtkinter as ctk
import serial
import threading
import serial.tools.list_ports
import time

# Inicialização do customtkinter
ctk.set_appearance_mode("dark")  # Define o modo de aparência (dark/light/system)
ctk.set_default_color_theme("blue")  # Define o tema de cor

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
            if e.args[0] == f"GetOverlappedResult failed (PermissionError(13, 'Acesso negado.', None, 5))" :
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
        except Exception as e:
            print(f"Erro ao desconectar: {e}")
       

# Interface CustomTkinter
root = ctk.CTk()
root.title("Monitor Serial Python by DALÇÓQUIO AUTOMAÇÃO")
root.geometry("1000x600")

# Frame para configurações
frame_config = ctk.CTkFrame(root)
frame_config.pack(pady=10)

# ComboBox para portas COM
com_label = ctk.CTkLabel(frame_config, font=new_fonte, text="Porta COM:")
com_label.grid(row=0, column=0, padx=3)
com_port_combo = ctk.CTkComboBox(frame_config, font=new_fonte, values=listar_portas(), width=150, state="readonly")
com_port_combo.grid(row=0, column=1, padx=3)

# Atualiza as portas COM no combo após criar a combobox
atualizar_com_port_combo()

# ComboBox para baudrate
baudrate_label = ctk.CTkLabel(frame_config, font=new_fonte, text="Baudrate:")
baudrate_label.grid(row=0, column=2, padx=3, pady=5)
baudrate_combo = ctk.CTkComboBox(frame_config, font=new_fonte, values=["1200", "2400", "4800", "9600",  "19200", "38400", "57600", "115200"], width=150, state="readonly")
baudrate_combo.grid(row=0, column=3, padx=3, pady=5)
baudrate_combo.set("9600")  # Seleciona 9600 por padrão

# Botão para conectar/desconectar
connect_button = ctk.CTkButton(frame_config, font=new_fonte, text="Conectar", command=conectar_serial, width=100)
connect_button.grid(row=0, column=4, padx=30, pady=10)

# Botão para scanear portas
scan_button = ctk.CTkButton(frame_config, font=new_fonte, text="Scanear", command=atualizar_com_port_combo, width=100)
scan_button.grid(row=0, column=5, padx=0, pady=10)

# Área de texto para exibir dados recebidos
text_area = ctk.CTkTextbox(root, font=new_fonte, width=1000, height=450)
text_area.pack()

# Função para exibir a tooltip
def show_tooltip(event):
    tooltip.place(x=event.x_root - root.winfo_rootx() + 20,
                  y=event.y_root - root.winfo_rooty() + 20)
    tooltip.lift()  # Garante que a tooltip fica em cima dos outros widgets

# Função para ocultar a tooltip
def hide_tooltip(event):
    tooltip.place_forget()

# Criando a tooltip (inicialmente invisível)
tooltip = ctk.CTkLabel(root, text="CTRL + A para selecionar, e DEL para deletar.")
tooltip.place_forget()

# Vinculando os eventos de mouse para mostrar e ocultar a tooltip
text_area.bind("<Enter>", show_tooltip)
text_area.bind("<Leave>", hide_tooltip)


# Frame para entrada e envio de dados
frame_entry = ctk.CTkFrame(root)
frame_entry.pack(pady=10)

# Entrada de texto para enviar dados
entry = ctk.CTkEntry(frame_entry, font=new_fonte, width=710)
entry.grid(row=0, column=0, padx=3, pady=10)

# Caracter para fim de linha
endline_combo = ctk.CTkComboBox(frame_entry, font=new_fonte, values=["None", "New Line", "Carriage Return", "Both NL and CR"], width=150, state="readonly")
endline_combo.grid(row=0, column=2, padx=3, pady=10)
endline_combo.set("None")

# Botão para enviar dados
send_button = ctk.CTkButton(frame_entry, font=new_fonte, text="Enviar", command=send_data, width=100)
send_button.grid(row=0, column=3, padx=10, pady=10)

# Enter para enviar dados
entry.bind('<Return>', lambda event: send_data())

root.mainloop()

# Fechar a porta serial ao encerrar o programa
if ser and ser.is_open:
    ser.close()
