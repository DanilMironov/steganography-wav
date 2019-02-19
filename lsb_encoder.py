import re
from lsb_stuff import LSBStuff as Stuff


class LSBEncoder:
    def __init__(self, path_to_file_to_insert: str, path_to_main_file: str):
        self.inserted_file = Stuff.read_the_file(path_to_file_to_insert)
        self.main_file = Stuff.read_the_file(path_to_main_file)
        self.index_of_start_of_data = \
            Stuff.find_index_of_the_start_of_data(self.main_file)
        self.bits_per_sample = self._get_bits_per_sample()
        self.inserted_file_name = self._define_filename(path_to_file_to_insert)

    def _check_the_opportunity_to_enter(self):
        record_unit = 2  # по сколько бит в сэмпл записывается
        free_bytes_count = len(self.main_file) - self.index_of_start_of_data
        # количество байтов основного файла куда можно записывать
        cells_to_write_count = (free_bytes_count * 8) // self.bits_per_sample
        # количество "ячеек" в которое можно записать
        necessary_count_of_cells = (len(self.inserted_file) * 8) // record_unit + 16
        return cells_to_write_count >= necessary_count_of_cells

    @staticmethod
    def _define_filename(path: str):
        name = re.search(r'\\?([ _0-9а-яА-Я\w]+[^\\]\w+)?$', path).group(1)
        return bytearray(bytes(name, 'utf-8'))

    def _get_bits_per_sample(self):
        byte34 = self.main_file[34].to_bytes(1, 'little')
        byte35 = self.main_file[35].to_bytes(1, 'little')
        bits_per_sample = int.from_bytes(byte34 + byte35, 'little')
        return bits_per_sample

    @staticmethod
    def change_byte_of_flag(data):
        pass

    @staticmethod
    def change_byte_of_data(data):
        pass

    def inscribe(self):
        bytes_to_describe_length_of_name = 16  # количество байт в которых хранится "длина" имени файла
        bits_of_name = Stuff.get_bin_str_from_bytearray(self.inserted_file_name)  # имя файла
        list_of_pairs_of_name = Stuff.split_in_two_bits(bits_of_name)  # список пар имени
        name_description = list(bin(len(list_of_pairs_of_name))[2:])  # список из длины имени файла
        while len(name_description) != bytes_to_describe_length_of_name:
            name_description = list('0') + name_description
        bytes_to_describe_length_of_data = 32
        bits_to_write = Stuff.get_bin_str_from_bytearray(self.inserted_file)  # строка которую записываем
        list_of_pairs_to_write = Stuff.split_in_two_bits(bits_to_write)  # список пар для записи
        length_description = list(bin(len(list_of_pairs_to_write))[2:])  # список из длины сообщения
        while len(length_description) != bytes_to_describe_length_of_data:
            length_description = list('0') + length_description  # дополняем список до длины 32
        offset = bytes_per_sample = self.bits_per_sample // 8
        index = self.index_of_start_of_data + bytes_per_sample - 1
        for i in range(bytes_to_describe_length_of_data):  # записали информацию о длине
            current_byte = self.main_file[index: index + 1]  # вытащили байт
            bin_repr_current_byte = Stuff.get_bin_str_from_bytearray(current_byte)
            list_of_current_chars = list(bin_repr_current_byte)
            list_of_current_chars[-1] = length_description[i]
            new_byte = Stuff.get_int_from_bin(''.join(list_of_current_chars))
            self.main_file[index] = new_byte
            index += offset
        for i in range(bytes_to_describe_length_of_name):  # записываем длину имени
            current_byte = self.main_file[index: index + 1]
            bin_repr_current_byte = Stuff.get_bin_str_from_bytearray(current_byte)
            list_of_current_chars = list(bin_repr_current_byte)
            list_of_current_chars[-1] = name_description[i]
            new_byte = Stuff.get_int_from_bin(''.join(list_of_current_chars))
            self.main_file[index] = new_byte
            index += offset
        for i in range(len(list_of_pairs_of_name)):
            current_byte = self.main_file[index: index + 1]
            bin_repr_current_byte = Stuff.get_bin_str_from_bytearray(current_byte)
            current_pairs = Stuff.split_in_two_bits(bin_repr_current_byte)
            current_pairs[-1] = list_of_pairs_of_name[i]
            new_byte = Stuff.get_int_from_bin(''.join(current_pairs))
            self.main_file[index] = new_byte
            index += offset
        for i in range(len(list_of_pairs_to_write)):
            current_byte = self.main_file[index: index + 1]  # вытащили байт
            bin_repr_current_byte = Stuff.get_bin_str_from_bytearray(current_byte)
            current_pairs = Stuff.split_in_two_bits(bin_repr_current_byte)  # разбили на пары символов
            current_pairs[-1] = list_of_pairs_to_write[i]  # изменили строку
            new_byte = Stuff.get_int_from_bin(''.join(current_pairs))  # собрали новый байт
            self.main_file[index] = new_byte  # засунули байт на место
            index += offset  # сдвигаемся к следующему байту
        with open('new_wav.wav', 'wb') as file:
            file.write(self.main_file)


if __name__ == '__main__':
    main = LSBEncoder('text.txt', 'Joy Division – New Dawn Fades.wav')
    main.inscribe()
