from dataclasses import dataclass
import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image
from pyparsing import col
from tkVideoPlayer import TkinterVideo
import yaml
from predict import recuperar_metadatos_modelos as get_metadatos_modelos
import predict
from dotenv import load_dotenv


load_dotenv('rutas_cfg')
RUTA_SALIDAS = os.getenv('RUTA_SALIDAS')
VENTANA_TITULO = 'Mantenimiento Vial con I.A.'
VENTANA_ANCHO = 1100
VENTANA_ALTO = 600


@dataclass
class ParamsDeteccion():
    confianza: float
    iou: float
         

class GUI():
    def __init__(self):
        # Setup main app window
        self.root = Tk()
        self.root.title(VENTANA_TITULO)
        self.root.geometry(f'{VENTANA_ANCHO}x{VENTANA_ALTO}')
        
        # Creates Main Content Frame
        self.input_params_frame = ttk.Frame(self.root).grid(column=0, row=0, sticky=(N, W, E, S))
        
        # Declarar variables sincronizadas
        self.crear_variables_deteccion()
        
        self.tab_configuracion = self.crear_frame_principal_entradas(parent_frame=self.input_params_frame)
        self.tab_configuracion.grid(column=0, row=0, sticky=(N,S,E,W), columnspan=2)
        
        
    def start(self):
        # Make it start the Event Loop
        self.root.mainloop()
        
    def crear_variables_deteccion(self):
        # REVISAR
        self.ruta_salida = StringVar(value=RUTA_SALIDAS)
        self.nombre_modelo = StringVar()
        self.confianza_var = DoubleVar()
        self.iou_var = DoubleVar()
        
        # Generales
        
        
        # Panel de pedido de ruta de entrada
        self.var_tipo_entrada_elegida = StringVar()
        self.ruta_entrada = StringVar()
        
        # Panel de modelo
        self.var_modelo_elegido = StringVar()
        
        # Panel etiquetas
        self.var_etiqueta_elegida = StringVar()
        self.var_modo_etiqueta_elegida = StringVar()
        
    def funcion_panel_pedido_ruta(self):
        if self.var_tipo_entrada_elegida.get() == 'Carpeta':
            self.entry_archivo.state(['disabled'])
            self.btn_archivo.state(['disabled'])
            self.entry_carpeta.state(['!disabled'])
            self.btn_carpeta.state(['!disabled'])
            return    
        
        if self.var_tipo_entrada_elegida.get() == 'Archivo':
            self.entry_carpeta.state(['disabled'])
            self.btn_carpeta.state(['disabled'])
            self.entry_archivo.state(['!disabled'])
            self.btn_archivo.state(['!disabled'])
            return    
        
    
    def preparar_llamada_y_llamar(self):
        print('Preparando llamada')
        ruta_archivo_generado = predict.run(self.ruta_entrada.get())
        ruta_archivo_generado = os.path.abspath(ruta_archivo_generado)
        print('Salida generada: ' + ruta_archivo_generado)
        
        if ruta_archivo_generado.split('.')[-1] == 'mp4':
            self.videoplayer.load(ruta_archivo_generado)
            self.videoplayer.pack(expand=True, fill="both")

            self.videoplayer.play() # play the video
        else:            
            image = Image.open(ruta_archivo_generado)
            image = ImageTk.PhotoImage(image)
            
            self.output_label.configure(image=image)
            self.output_label.image=image
            # image = PhotoImage(file=ruta_archivo_generado)
            # ttk.Label(self.tab_configuracion, image=image).grid(column=0, row=6, sticky=(W,E,N,S))
            
   
    def crear_frame_principal_entradas(self, parent_frame):
        frame_config_parametros = ttk.Frame(parent_frame)
        
        styling_grid = {}
        
        self.crear_panel_pedido_ruta(frame_config_parametros).grid(column=0, row=0, columnspan=3, **styling_grid)
        self.crear_panel_modelo(frame_config_parametros).grid(column=0, row=1, **styling_grid)
        self.crear_panel_deteccion_cfg(frame_config_parametros).grid(column=0, row=2, **styling_grid)
        self.crear_panel_etiquetas(frame_config_parametros).grid(column=1, row=1, rowspan=2, **styling_grid)
        self.crear_panel_parametros_entrenamiento(frame_config_parametros).grid(column=2, row=1, rowspan=2, **styling_grid)
        
        for frame in frame_config_parametros.winfo_children():
            frame['borderwidth'] = 2,
            frame['relief'] = 'raised',
            frame['padding'] = (10,5)
        
        ttk.Button(frame_config_parametros,text='Inferir', width=20, command=self.preparar_llamada_y_llamar).grid(column=0, row=3)
        
        return frame_config_parametros
    
    def crear_panel_pedido_ruta(self, parent_frame) -> ttk.Frame:
        ANCHO_CAMPO_TEXTO = 80
        
        frame = ttk.Frame(parent_frame)
        
        ttk.Label(frame, text='Elegir entrada').grid(column=0, row=0)
        # Control para entrada de carpeta
        ttk.Radiobutton(frame, text='Carpeta', variable=self.var_tipo_entrada_elegida, value='Carpeta',command=self.funcion_panel_pedido_ruta).grid(column=0, row=1)
        self.entry_carpeta = ttk.Entry(frame, width=ANCHO_CAMPO_TEXTO, textvariable=self.ruta_entrada)
        self.entry_carpeta.grid(column=1, row=1)
        self.btn_carpeta = ttk.Button(frame,text='Seleccionar', command=lambda: self.ruta_entrada.set(filedialog.askdirectory()))
        self.btn_carpeta.grid(column=2, row=1)
       
        # Control para entrada de archivo
        ttk.Radiobutton(frame, text='Archivo', variable=self.var_tipo_entrada_elegida, value='Archivo',command=self.funcion_panel_pedido_ruta).grid(column=0, row=2)
        self.entry_archivo = ttk.Entry(frame, width=ANCHO_CAMPO_TEXTO, textvariable=self.ruta_entrada)
        self.entry_archivo.grid(column=1, row=2)
        self.btn_archivo = ttk.Button(frame,text='Seleccionar', command=lambda: self.ruta_entrada.set(filedialog.askopenfilename()))
        self.btn_archivo.grid(column=2, row=2)
        
        return frame
    
    
    def crear_panel_modelo(self, parent_frame) -> ttk.Frame:
        frame = ttk.Frame(parent_frame)
        lista_nombres_modelos = [metadatos.nombre for metadatos in get_metadatos_modelos()]
        
        self.var_modelo_elegido.set(lista_nombres_modelos[0])
        
        ttk.Label(frame, text='Modelo').grid(column=0, row=0)
        combo = ttk.Combobox(frame, values=lista_nombres_modelos, textvariable=self.var_modelo_elegido)
        combo.bind('<<ComboboxSelected>>', self.recrear_panel_etiquetas)
        combo.grid(column=0, row=1)
        
        return frame
    
    def crear_panel_deteccion_cfg(self, parent_frame) -> ttk.Frame:
        var_iou_elegido = DoubleVar(value=0.25)
        var_confianza_elegida = DoubleVar(value=0.20)
        frame = ttk.Frame(parent_frame)
        
        ttk.Label(frame, text='Parametros de inferencia').grid(column=0, row=0)
        ttk.Label(frame, text='IOU').grid(column=0, row=1)
        ttk.Entry(frame, textvariable=var_iou_elegido, width=10).grid(column=1, row=1)
        ttk.Label(frame, text='Confianza').grid(column=0, row=2)
        ttk.Entry(frame, textvariable=var_confianza_elegida, width=10).grid(column=1, row=2)
        
        return frame
    
    def crear_panel_etiquetas(self, parent_frame) -> ttk.Frame:
        modelo_elegido = self.var_modelo_elegido.get()
        lista_etiquetas = predict.get_lista_etiquetas(nombre_modelo = modelo_elegido)
        
        frame = ttk.Frame(parent_frame)
        
        ttk.Label(frame, text='Etiquetas').grid(column=0, row=0)
        ttk.Radiobutton(frame, text='Incluir', variable=self.var_modo_etiqueta_elegida, value='Incluir').grid(column=0, row=1)
        ttk.Radiobutton(frame, text='Excluir', variable=self.var_modo_etiqueta_elegida, value='Excluir').grid(column=1, row=1)
        
        for idx in range(10):
            if idx < len(lista_etiquetas):
                ttk.Checkbutton(frame, text=lista_etiquetas[idx], variable=self.var_etiqueta_elegida).grid(column=0, row=2+idx, sticky=(E,W))
            else:
                ttk.Checkbutton(frame, text='Sin definir', variable=self.var_etiqueta_elegida, state='disabled').grid(column=0, row=2+idx, sticky=(E,W))
        return frame
    
    def crear_panel_parametros_entrenamiento(self, parent_frame) -> ttk.Frame:
        ruta_base = os.getenv('RUTA_BASE_MODELOS')
        ruta_opts = ruta_base + '/' + self.var_modelo_elegido.get() + '/opt.yaml'
        file = open(ruta_opts, 'r')
        training_params:dict = yaml.load(file, Loader=yaml.SafeLoader)
        training_params = yaml.dump(training_params, line_break='\n')
        frame = ttk.Frame(parent_frame)
        
        ttk.Label(frame, text='Parametros de entrenamiento').grid(column=0, row=0)
        widget_params_entrenamiento = Text(frame, width=40)
        widget_params_entrenamiento.grid(column=0, row=1)
        
        widget_params_entrenamiento.insert('0.0', training_params)        
        
        return frame
    
    def recrear_panel_etiquetas(self, other_var):
        print(f'other_var: {other_var}')
        self.panel_etiquetas = self.crear_panel_etiquetas(self.tab_configuracion)
        self.panel_etiquetas.grid(column=1, row=1, rowspan=2)
        
if __name__ == '__main__':
    gui = GUI()
    gui.start()