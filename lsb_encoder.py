from lsb_stuff import LSBStuff as stuff


class LSBEncoder:
    def __init__(self, path_to_file_to_insert: str, path_to_main_file: str):
        self.inserted_file = stuff.read_the_file(path_to_file_to_insert)
        self.main_file = stuff.read_the_file(path_to_main_file)
        self.index_of_start_of_data = \
            stuff.find_index_of_the_start_of_data(self.main_file)
        self.bits_per_sample = self._get_bits_per_sample()

    @staticmethod
    def _find_index_of_the_start_of_data(list_of_bytes: bytearray):
        offset = 8
        res = list_of_bytes.find(b'data')
        return res + offset

    @staticmethod
    def _read_the_file(path_to_the_file):
        with open(path_to_the_file, 'rb') as file:
            data = bytearray(file.read())
        return data

    def _check_the_opportunity_to_enter(self):
        record_unit = 2  # по сколько бит в сэмпл записывается
        free_bytes_count = len(self.main_file) - self.index_of_start_of_data
        # количество байтов основного файла куда можно записывать
        cells_to_write_count = (free_bytes_count * 8) // self.bits_per_sample
        # количество "ячеек" в которое можно записать
        necessary_count_of_cells = (len(self.inserted_file) * 8) // record_unit + 16
        return cells_to_write_count >= necessary_count_of_cells

    def _get_bits_per_sample(self):
        byte34 = self.main_file[34].to_bytes(1, 'little')
        byte35 = self.main_file[35].to_bytes(1, 'little')
        bits_per_sample = int.from_bytes(byte34 + byte35, 'little')
        return bits_per_sample

    @staticmethod
    def _get_bin_str_from_bytearray(data: bytearray):
        bin_str = ''.join('{}'.format(bin(e)[2:]) for e in data)
        while len(bin_str) % 8 != 0:
            bin_str = '0' + bin_str
        return bin_str

    @staticmethod
    def _get_bin_from_int(byte):
        bin_str = bin(byte)[2:]
        while len(bin_str) % 8 != 0:
            bin_str = '0' + bin_str
        return bin_str

    @staticmethod
    def _split_the_string_into_chars(string):
        return list(string)

    @staticmethod
    def _split_in_two_bits(string):
        list_of_pair = []
        for i in range(len(string) // 2):
            list_of_pair.append(string[2 * i:2 * i + 2])
        return list_of_pair

    @staticmethod
    def _get_int_from_bin(bin_str):
        return int(bin_str, 2)

    def inscribe(self):
        bytes_to_describe_length = 32
        bits_to_write = stuff.get_bin_str_from_bytearray(self.inserted_file)  # строка которую записываем
        list_of_pairs_to_write = stuff.split_in_two_bits(bits_to_write)  # список пар для записи
        length_description = list(bin(len(list_of_pairs_to_write))[2:])  # список из длины сообщения
        while len(length_description) != bytes_to_describe_length:
            length_description = list('0') + length_description  # дополняем список до длины 32
        offset = bytes_per_sample = self.bits_per_sample // 8
        index = self.index_of_start_of_data + bytes_per_sample - 1
        for i in range(bytes_to_describe_length):  # записали информацию о длине
            current_byte = self.main_file[index: index + 1]  # вытащили байт
            bin_repr_current_byte = stuff.get_bin_str_from_bytearray(current_byte)
            list_of_current_chars = list(bin_repr_current_byte)
            list_of_current_chars[-1] = length_description[i]
            new_byte = stuff.get_int_from_bin(''.join(list_of_current_chars))
            self.main_file[index] = new_byte
            index += offset
        for i in range(len(list_of_pairs_to_write)):
            current_byte = self.main_file[index:index+1]  # вытащили байт
            # bin_repr_current_byte = self._get_bin_from_byte(current_byte)  # получили бинарную строку
            bin_repr_current_byte = stuff.get_bin_str_from_bytearray(current_byte)
            current_pairs = stuff.split_in_two_bits(bin_repr_current_byte)  # разбили на пары символов
            current_pairs[-1] = list_of_pairs_to_write[i]  # изменили строку
            new_byte = stuff.get_int_from_bin(''.join(current_pairs))  # собрали новый байт
            self.main_file[index] = new_byte  # засунули байт на место
            index += offset  # сдвигаемся к следующему байту
        with open('new_wav.wav', 'wb') as file:
            file.write(self.main_file)


if __name__ == '__main__':
    main = LSBEncoder('text.txt', 'Joy Division – New Dawn Fades.wav')
    main.inscribe()
