import tkinter as tk
from tkinter import messagebox

from pylogix import PLC

import logging

import json

import time

import os

import threading

import sys

from PIL import Image, ImageTk

from ftplib import FTP

import cv2

import numpy as np

import datetime

import shutil

from flask_caching import Cache

from flask import Flask

import gc

import csv

from keras.models import load_model

import tensorflow as tf

app = Flask(__name__)
config = {'CACHE_TYPE': 'simple'}
cache = Cache(app, config==config)

system_name = os.name

logging.basicConfig(filename="logger.log", level=logging.ERROR,
                    format="%(asctime)s - %(levelname)s- %(message)s",
                    encoding="utf-8")

months = [ "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

try:
    config_variables = []
    with open("Resources/config.json", "r") as config_file:
        config_variables = json.load(config_file)
        config_file.close()
    print("Config file loaded correctly!!!")
    time.sleep(1)
except Exception as e:
    logging.exception(e)
    time.sleep(30)
    exit()

comm1 = PLC()
comm2 = PLC()

comm1.IPAddress = config_variables["plc_ip_address"]
comm2.IPAddress = config_variables["plc_ip_address"]

plc_out_comm_status_tag = config_variables["out_plc_status_tag"]
plc_in_comm_status_tag = config_variables["in_plc_status_tag"]

class send_status_to_plc(threading.Thread):
    def __init__(self):
        super().__init__()
        self.StopEvent = threading.Event()
    def run(self):
        try:
            while not self.StopEvent.is_set():
                comm1.Write(plc_in_comm_status_tag, 1)
                time.sleep(1)
                comm1.Write(plc_in_comm_status_tag, 0)
                time.sleep(1)
                comm1.Close()
        except Exception as e:
            logging.exception(e)
            exit()
    def stop(self):
        self.StopEvent.set()

class read_status_from_plc(threading.Thread):
    def __init__(self, update_callback):
        super(read_status_from_plc, self).__init__()
        self.update_callback = update_callback
        self.StopEvent = threading.Event()
    def run(self):
        try:
            while not self.StopEvent.is_set():
                self.plc_comm_state = comm2.Read(plc_out_comm_status_tag).Value
                plc_comm_status = comm2.Read(plc_out_comm_status_tag).Value
                self.update_callback(plc_comm_status)
                time.sleep(0.25)
                comm2.Close()
        except Exception as e:
            logging.exception(e)
            exit()
    def stop(self):
        self.StopEvent.set()

class view:
    def __init__(self, window):
        self.root = window
        self.init_tkinter()
        self.show_info_dialog('App Ready', 'Corriendo App...')
        self.display_minimized = False
        self.read_variables_from_file()

    def init_tkinter(self):
        try:
            """Initialitation of main screen"""
            self.root.title("Pin Reservoir Hole TCM8L6")
            self.root.overrideredirect(True)
            self.root.geometry("800x480+0+0")
            self.root.protocol("WM_DELETE_WINDOW", self.exit)
            if system_name == "nt":
                self.root.iconbitmap("Resources/AI.ico")
            # self.root.resizable(0,0)
            self.root.configure(background='#ffffff')

            """PLC Status"""
            self.status_plc_label = tk.Label(self.root, text='PLC Communication', font=("Arial", 12), relief='flat')
            self.status_plc_label.place(x= 380, y= 350)
            self.status_plc_label.configure(background='#ffffff')
            self.status_plc_indicator = tk.Label(self.root, bg='#005500')
            self.status_plc_indicator.place(x=350, y=350, width=20, height=20)

            """Save Image"""
            self.save_image_label = tk.Label(self.root, text='Save Image', font=("Arial", 12), relief='flat')
            self.save_image_label.place(x= 380, y= 380)
            self.save_image_label.configure(background='#ffffff')
            self.save_image_indicator = tk.Label(self.root, bg='#005500')
            self.save_image_indicator.place(x=350, y=380, width=20, height=20)

            """Main Title"""
            self.title_label = tk.Label(self.root, text='Pin Reservoir Hole TCM8L6', font=("Arial", 20, 'bold'), relief='flat')
            self.title_label.place(x= 270, y= 20)
            self.title_label.configure(background='#ffffff')

            """Super Color Image"""
            self.super_color_image = Image.open('Resources/SuperColor.jpg')
            self.super_color = ImageTk.PhotoImage(self.super_color_image)
            self.super_color_label = tk.Label(self.root)
            self.super_color_label.configure(image=self.super_color)
            self.super_color_label.image = self.super_color
            self.super_color_label.place(x=0, y=0)

            """IAguP Logo"""
            self.agup_image = Image.open('Resources/IAguP_Logo.png')
            self.agup = ImageTk.PhotoImage(self.agup_image)
            self.agup_label = tk.Label(self.root)
            self.agup_label.configure(image=self.agup)
            self.agup_label.image = self.agup
            self.agup_label.place(x=0, y=10)

            """"DATA Logo"""
            self.data_image = Image.open('Resources/DATA.jpg')
            self.data = ImageTk.PhotoImage(self.data_image)
            self.data_label = tk.Label(self.root)
            self.data_label.configure(image=self.data)
            self.data_label.image = self.data
            self.data_label.place(x=730, y=10)

            """Result Image"""
            self.result_image = tk.Label(self.root, bg='#ffffff')
            self.result_image.place(x=20, y=100, height=300, width=300)

            self.top_line_frame = tk.Label(self.root, bg='#ffffff')
            self.top_line_frame.place(x=10, y=90, width=320, height=10)

            self.left_line_frame = tk.Label(self.root, bg='#ffffff')
            self.left_line_frame.place(x=10, y=90, width=10, height=320)

            self.down_line_frame = tk.Label(self.root, bg='#ffffff')
            self.down_line_frame.place(x=10, y=400, width=320, height=10)

            self.right_line_frame = tk.Label(self.root, bg='#ffffff')
            self.right_line_frame.place(x=320, y=90, width=10, height=320)

            """Part Number Label"""
            self.pn_label = tk.Label(self.root, bg='#ffffff', text='Número de Parte: ',
                                    font=('Bosch Sans Global', 14, 'bold'))
            self.pn_label.place(x=350, y=90)

            """Datamatrix Label"""
            self.data_matrix_label = tk.Label(self.root, bg='#ffffff', text='Datamatrix: ',
                                    font=('Bosch Sans Global', 14, 'bold'))
            self.data_matrix_label.place(x=350, y=120)

            """Job Camera Label"""
            self.job_number_label = tk.Label(self.root, bg='#ffffff', text='Job de Camara: ',
                                    font=('Bosch Sans Global', 14, 'bold'))
            self.job_number_label.place(x=350, y=150)

            """Result AI String Label"""
            self.result_string_label = tk.Label(self.root, bg='#ffffff', text='',
                                    font=('Bosch Sans Global', 14, 'bold'))
            self.result_string_label.place(x=350, y=180, width=300)

            """Result AI INT Label"""
            self.result_int_label = tk.Label(self.root, bg='#ffffff', text='',
                                    font=('Bosch Sans Global', 14, 'bold'))
            self.result_int_label.place(x=350, y=210, width=300)

            """Result AI Label"""
            self.ai_result_label = tk.Label(self.root, bg='#ffffff', text='',
                                    font=('Bosch Sans Global', 14, 'bold'))
            self.ai_result_label.place(x=350, y=240)

            """Execution Time Label"""
            self.execution_time_label = tk.Label(self.root, bg='#ffffff',
                                                text='Tiempo de Ejecución AI: ',
                                                font=('Bosch Sans Global', 14, 'bold'))
            self.execution_time_label.place(x=350, y=270)

            """Exit button"""
            self.exit_button = tk.Button(self.root, bg= "#ff0000", text="Salir",
                                         font=('Bosch Sans Global', 14, 'bold'),
                                         fg="#ffffff",command=self.exit)
            self.exit_button.place(x=700, y=420, width=80, height=40)
        except Exception as e:
            self.register_error('App Setting error','Error al abrir la app' + str(e), e)
            self.exit()
            sys.exit()

    def read_variables_from_file(self):
        self.variables_from_file = []
        try:
            with open("Resources/config.json", "r") as config_file2:
                self.variables_from_file = json.load(config_file2)
                config_file2.close()
            if len(self.variables_from_file) == 0:
                self.register_error("Config File Empty",
                                    "Archivo de Configuración vacío!!!",
                                    "Error: Archivo de Configuración vacío!!!")
                self.exit()
                sys.exit()
            self.show_info_dialog("Config File Loaded", "Archivo de Configuración Cargado!!!")
        except FileNotFoundError:
            self.register_error('Load Variables Error',
                                'Error al cargar archivo de configuración', str(e))
            self.exit()
            sys.exit()

        self.root.after(150, self.load_plc_params)

    def load_plc_params(self):
        self.comm = PLC()
        self.comm.IPAddress = self.variables_from_file["plc_ip_address"]
        self.plc_out_comm_status_tag = self.variables_from_file["out_plc_status_tag"]
        self.plc_in_comm_status_tag = self.variables_from_file["in_plc_status_tag"]
        self.enable_ai_inspection_tag = self.variables_from_file["enable_ai_inspection_tag"]
        self.ai_trigger_tag = self.variables_from_file["ai_trigger_tag"]
        self.result_to_plc_tag = self.variables_from_file["result_to_plc_tag"]
        self.cycle_running_tag = self.variables_from_file["cycle_running_tag"]
        self.enable_save_images_tag = self.variables_from_file["enable_save_images_tag"]
        self.part_number_tag = self.variables_from_file["part_number_tag"]
        self.data_matrix_tag = self.variables_from_file["data_matrix_tag"]
        self.job_number_tag = self.variables_from_file["job_number_tag"]
        self.ai_finished_tag = self.variables_from_file["ai_finished_tag"]

        self.root.after(150, self.connect_to_plc)

    def connect_to_plc(self):
        try:
            communication_test = self.comm.Read(self.plc_out_comm_status_tag).Value
            if communication_test is not None:
                self.show_info_dialog("PLC Communication",
                                      "Se estableció comunicaicón con PLC")
            else:
                self.register_error("PLC Communication",
                                    "Error en comunicación con el PLC",
                                    "Error en comunicación con el PLC")
                self.exit()
                sys.exit()
            self.comm.Close()
        except Exception as e:
            self.register_error('Communication',
                               ('Error en Comunicación con PLC ' + str(e)),
                               ('Error: ' + str(e)))
            self.exit()
            sys.exit()

        self.root.after(150, self.load_variables)

    def load_variables(self):
        self.img_height, self.img_width = 300, 300
        if not os.path.exists("Resources/ID.txt"):
            with open("Resources/ID.txt", "w") as new_file_id:
                new_file_id.write("0")
                new_file_id.close()
        if not os.path.exists("Resources/results_db.csv"):
            text_to_save = "Image ID;Part Number;Job Number;Result; OK/NOK; Result ID; AI Result; Date"
            with open("Resources/results_db.csv", "w", newline="") as new_file_results:
                writer = csv.writer(new_file_results)
                writer.writerow(text_to_save.strip().split(","))
        self.camera_ip_address = self.variables_from_file["camera_ip_address"]
        self.camera_user = self.variables_from_file["camera_user"]
        self.camera_pass = self.variables_from_file["camera_pass"]
        self.path_to_move_images = self.variables_from_file["path_to_move_images"]
        os.makedirs(self.path_to_move_images, exist_ok=True)

        self.root.after(150, self.start_thread)

    def start_thread(self):
        self.read_status_from_plc = read_status_from_plc(self.update_status_indicator_thread)
        self.send_status_to_plc = send_status_to_plc()
        self.read_status_from_plc.start()
        self.send_status_to_plc.start()
        self.root.after(150, self.main_program)

    def main_program(self):
        self.read_tags_from_plc()

        if self.cycle_running:
            self.read_trigger_tags()
            if not self.ai_trigger and self.result_to_plc == 0:
                self.reset_indicators()
            if self.ai_trigger and self.result_to_plc == 0 and self.enable_ai_inspection:
                self.load_part_number_setup()
                self.start_time = time.time()
                self.get_image_from_camera()
                self.assign_path_image()
                self.start_ai()
                self.write_to_plc()
                cache.clear()
                gc.collect()

        else:
            self.display_minimized = False
        self.root.after(150, self.main_program)

    def show_display(self):
        self.root.deiconify()
        self.root.geometry("1440x850+0+0")
        self.display_minimized = True

    def hide_display(self):
        self.root.iconify()
        self.display_minimized = True

    def read_tags_from_plc(self):
        self.cycle_running = self.comm.Read(self.cycle_running_tag).Value
        self.enable_save_images = self.comm.Read(self.enable_save_images_tag).Value
        self.part_number = self.comm.Read(self.part_number_tag).Value
        self.data_matrix = self.comm.Read(self.data_matrix_tag).Value
        self.job_number = self.comm.Read(self.job_number_tag).Value
        self.display_state = self.root.state()
        self.comm.Close()
        self.update_status_indicator()

    def update_status_indicator(self):
        self.pn_label.configure(text=f"Número de Parte: {self.part_number}",
                                font=('Bosch Sans Global', 14, 'bold'))
        self.data_matrix_label.configure(text=f"Datamatrix: {str(self.data_matrix)}",
                                    font=('Bosch Sans Global', 14, 'bold'))
        self.job_number_label.configure(text=f"Job de Camara: {str(self.job_number)}",
                                 font=('Bosch Sans Global', 14, 'bold'))
        if self.enable_save_images:
            self.save_image_indicator.configure(bg='#00ff00')
            self.save_image_label.configure(text='Guardando Imágenes', font=("Arial", 12))
        else:
            self.save_image_indicator.configure(bg='#005500')
            self.save_image_label.configure(text='Guardado Deshabilitado', font=("Arial", 12))

    def read_trigger_tags(self):
        self.enable_ai_inspection = self.comm.Read(self.enable_ai_inspection_tag).Value
        self.ai_trigger = self.comm.Read(self.ai_trigger_tag).Value
        self.result_to_plc = self.comm.Read(self.result_to_plc_tag).Value
        self.comm.Close()

    def reset_indicators(self):
        self.top_line_frame.configure(bg='#ffffff')
        self.down_line_frame.configure(bg='#ffffff')
        self.left_line_frame.configure(bg='#ffffff')
        self.right_line_frame.configure(bg='#ffffff')
        self.result_string_label.configure(text='', bg='#ffffff')
        self.result_int_label.configure(text='', bg='#ffffff')
        self.ai_result_label.configure(text='Resultado de AI: ')
        self.execution_time_label.configure(text='Tiempo de Ejecución AI: ')
        self.result_image.configure(image='')

    def load_part_number_setup(self):
        try:
            self.read_part_number_setup()
            self.setup_part_number = self.setup_variables[str(self.job_number)] # use only in production
            # self.setup_part_number = self.setup_variables[str(10)]
            self.model_file_path = self.setup_part_number["ai_model"]
            self.img_height_crop = self.setup_part_number["img_height_crop"]
            self.img_width_crop = self.setup_part_number["img_width_crop"]
            self.img_height_init_pixel = self.setup_part_number["img_height_init_pixel"]
            self.img_width_init_pixel = self.setup_part_number["img_width_init_pixel"]
            self.img_height_end_pixel = self.img_height_init_pixel + self.img_height_crop
            self.img_width_end_pixel = self.img_width_init_pixel + self.img_width_crop
            self.evaluation_model = self.setup_part_number["evaluations"]
            self.model = load_model(self.model_file_path)
            # self.interpreter = tf.lite.Interpreter(self.model_file_path)
            # self.interpreter.allocate_tensors()
            # self.input_details = self.interpreter.get_input_details()
            # self.output_details = self.interpreter.get_output_details()

        except Exception as e:
            self.register_error('Load Part Number Setup Error','Error: ' + str(e),'Error: '+str(e))
            self.exit()
            sys.exit()

    def read_part_number_setup(self):
        try:
            with open("Resources/setup.json", "r") as setup_file:
                self.setup_variables = json.load(setup_file)
                setup_file.close()
            if len(self.setup_variables) == 0:
                self.register_error('Setup File empty', 'Archivo de setup vacío!!!',
                                    'Error: Archivo de Setup vacío!!!')
                self.exit()
                sys.exit()
        except Exception as e:
            self.register_error('Read Setup File',
                                'Error al leer Archivo de setup de este número de parte: ' + str(e),
                                'Error al leer archivo de setup de este número de parte: ' + str(e))
            self.exit()
            sys.exit()

    def assign_path_image(self):
        pass

    def start_ai(self):
        self.image_processing()
        self.prediction()
        end_time = time.time()
        self.elapse_time = f"{(end_time - self.start_time):.2f}"
        self.update_main_screen()
        self.save_results()
        self.remove_images()

    def image_processing(self):
        image = cv2.imread("image.jpg")
        image_rotated = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        cv2.imwrite("image.jpg", image_rotated)
        image_processed = image_rotated[self.img_height_init_pixel:self.img_height_end_pixel,
                                          self.img_width_init_pixel:self.img_width_end_pixel]
        cv2.imwrite("image_cropped.jpg", image_processed)
        image_to_predict = cv2.imread("image_cropped.jpg")
        image_normalized = (np.asanyarray(image_to_predict)) / 255
        self.image_expanded = np.expand_dims(image_normalized, axis=0).astype(np.float32)

    def prediction(self):
        # self.interpreter.set_tensor(self.input_details[0]["index"], self.image_expanded)
        # self.interpreter.invoke()
        # output_raw = self.interpreter.get_tensor(self.output_details[0]["index"])
        output_raw = self.model.predict(self.image_expanded)
        output = np.squeeze(output_raw)
        self.max_value = None
        self.max_idx = -1

        for idx, num in enumerate(output):
            if (self.max_value is None or num > self.max_value):
                self.max_value = num
                self.max_idx = idx

        self.result_label = self.evaluation_model[str(self.max_idx)]["label"]
        self.result_value = self.evaluation_model[str(self.max_idx)]["result"]
        self.min_score = self.evaluation_model[str(self.max_idx)]["min_score"]
        self.max_score = self.evaluation_model[str(self.max_idx)]["max_score"]

        if self.result_value == "OK":
            if (self.max_value >= self.min_score) and (self.max_value <= self.max_score):
                self.ai_result = 1
            else:
                self.ai_result = 3
        else:
            self.ai_result = 2

    def update_main_screen(self):
        if self.ai_result == 1:
            frame_color = "#00ff00" # Use in production
            text_color = "#000000"
            self.text_result = self.result_label
        elif self.ai_result == 2:
            frame_color = "#ff0000"
            text_color = "#ffffff"
            self.text_result = self.result_label
        elif self.ai_result == 3:
            frame_color = "#dcdc00"
            text_color = "#000000"
            self.text_result = "Incertidumbre"

        self.top_line_frame.configure(bg=frame_color)
        self.down_line_frame.configure(bg=frame_color)
        self.left_line_frame.configure(bg=frame_color)
        self.right_line_frame.configure(bg=frame_color)

        self.result_string_label.configure(bg=frame_color, text=self.text_result,
                                 font=('Bosch Sans Global', 14, 'bold'),
                                 fg=text_color)
        # self.result_string_label.place(x=860, y=240, width=200, height=60)

        self.result_int_label.configure(bg=frame_color,
                                 font=('Bosch Sans Global', 14, 'bold'),
                                 fg=text_color, text=("Tipo de barreno: " +
                                                     str(self.max_idx) + ", " + str(self.job_number)))
        # self.result_int_label.place(x=860, y=330, width=200, height=60)

        self.ai_result_label.configure(text=('Resultado de AI: ' + str(f"{(self.max_score * 100):.2f} %")),
                                       font=('Bosch Sans Global', 14, 'bold'))

        self.execution_time_label.configure(text=('Tiempo de Ejecución AI: ' +
                                                  str(self.elapse_time) + ' Seg'))
        image_new = cv2.imread("image_cropped.jpg")
        image_resized = cv2.resize(image_new, (self.img_width, self.img_height))
        cv2.imwrite("image_resized.jpg", image_resized)
        self.result_image_aux = Image.open("image_resized.jpg")
        self.result_image_aux2 = ImageTk.PhotoImage(self.result_image_aux)
        self.result_image.configure(image=self.result_image_aux2)
        self.result_image.image = self.result_image_aux2

    def get_image_from_camera(self):
        try:
            self.ftp_camera = FTP(self.camera_ip_address)
            self.ftp_camera.login(self.camera_user, self.camera_pass)
            file_name = "image.jpg"
            with open(file_name, "wb") as camera_comm:
                self.ftp_camera.retrbinary("RETR " + file_name, camera_comm.write)
                camera_comm.close()
        except Exception as e:
            self.register_error('FTP Error', 'Error en comunicación FTP: ' + str(e),
                                ('Error: ' + str(e)))
            self.exit()
            sys.exit()

    def save_results(self):
        self.read_id()
        self.get_date_time()
        self.text_to_save = (str(self.img_id).zfill(6) + ";" + self.part_number + ";" + str(self.job_number)
                             + ";" + self.text_result + self.result_value + ";" + str(self.max_idx) + ";" +
                             str(f"{self.max_score:.5f}") +";" + self.current_date + ";")
        with open("Resources/results_db.csv", "a", newline="") as append_file:
            writer = csv.writer(append_file)
            writer.writerow(self.text_to_save.strip().split(","))

        self.path_to_save = (str(self.img_id).zfill(6) + "_" + str(self.job_number).zfill(3) +
                             "_" + self.text_result + self.result_value + "_" +
                             str(self.max_idx).zfill(3) + "_" + str(f"{self.max_score:.5f}") +
                             "_" + self.current_date2)
        image_complete_name = self.path_to_save + ".jpg"
        image_cropped_name = self.path_to_save + "_cropped.jpg"
        part_number_path = os.path.join(self.path_to_move_images, self.part_number)
        completed_path = os.path.join(part_number_path, "Complete")
        os.makedirs(completed_path, exist_ok=True)
        cropped_path = os.path.join(part_number_path, "Cropped")
        os.makedirs(cropped_path, exist_ok=True)
        self.path_to_move_image_complete = os.path.join(completed_path, image_complete_name)
        self.path_to_move_image_cropped = os.path.join(cropped_path, image_cropped_name)
        if self.img_id <= 999999:
            self.img_id += 1
        else:
            self.img_id = 0
        self.write_id()

    def read_id(self):
        with open("Resources/ID.txt", "r") as file_id_read:
            self.img_id = int(file_id_read.read().strip())
            file_id_read.close()

    def write_id(self):
        with open("Resources/ID.txt", "w") as file_id_write:
            file_id_write.write(str(self.img_id))
            file_id_write.close()

    def get_date_time(self):
        current_date = datetime.datetime.now()
        current_year = str(current_date.year)
        current_year_2dig = str(current_year[2:4])
        current_month = str(current_date.month).zfill(2)
        current_day = str(current_date.day).zfill(2)
        current_hour = str(current_date.hour).zfill(2)
        current_minute = str(current_date.minute).zfill(2)
        current_second = str(current_date.second).zfill(2)

        num_month = 0
        current_month_str = ""
        current_month_dint = current_date.month
        for num_month in range(12):
            if num_month == (current_month_dint - 1):
                current_month_str = months[num_month]
        date_completed = current_day + current_month_str + current_year_2dig
        time_completed = current_hour + "_" + current_minute + "_" + current_second
        self.current_date = (current_year + "_" + current_month + "_" + current_day + "_" +
                            current_hour  + ":" + current_minute + ":" + current_second)
        self.current_date2 = date_completed + time_completed

    def remove_images(self):
        if self.enable_save_images:
            shutil.move("image.jpg", self.path_to_move_image_complete)
            shutil.move("image_cropped.jpg", self.path_to_move_image_cropped)
        else:
            os.remove("image.jpg")
            os.remove("image_cropped.jpg")
        os.remove("image_resized.jpg")

    def write_to_plc(self):
        self.comm.Write(self.ai_trigger_tag, 0)
        self.comm.Write(self.ai_finished_tag, 1)
        self.comm.Write(self.result_to_plc_tag, self.ai_result)
        self.comm.Close()

    def update_status_indicator_thread(self, plc_comm_state):
        if self.read_status_from_plc.plc_comm_state:
            self.status_plc_indicator.config(bg='#00ff00')
        else:
            self.status_plc_indicator.config(bg='#005500')

    def show_error_dialog(self, error_title, error_text):
        if system_name == "nt":
            messagebox.showerror(error_title, error_text)
        else:
            print(error_text)

    def show_info_dialog(self, window_title, text_info):
        if system_name == "nt":
            messagebox.showinfo(title=window_title, message=text_info)
        else:
            print(text_info)
        logging.info(text_info)

    def register_error(self, dialog_error_name, dialog_error_text, logging_error_text):
        self.show_error_dialog(dialog_error_name, dialog_error_text)
        logging.exception(logging_error_text)

    def exit(self):
        window.destroy()
        self.send_status_to_plc.stop()
        self.read_status_from_plc.stop()

if __name__ == "__main__":
    window = tk.Tk()
    app = view(window)
    window.mainloop()

def start_main():
    window = tk.Tk()
    app = view(window)
    window.mainloop()