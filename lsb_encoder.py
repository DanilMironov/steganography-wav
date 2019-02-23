import re
from lsb_stuff import LSBStuff as Stuff


class LSBEncoder:
    def __init__(self, path_to_file_to_insert: str, path_to_main_file: str):
        self.inserted_file = Stuff.read_the_file(path_to_file_to_insert)
        self.main_file = Stuff.read_the_file(path_to_main_file)
        if not self._check_the_opportunity_to_enter():
            raise Exception("The file you want to write is too large")
        self.index_of_start_of_data = \
            Stuff.find_index_of_the_start_of_data(self.main_file)
        self.bits_per_sample = self._get_bits_per_sample(self.main_file)
        self.inserted_name = self._define_filename(path_to_file_to_insert)
        self.inserted_hash = Stuff.get_hash(self.inserted_file)

    def _check_the_opportunity_to_enter(self):
        record_unit = 1
        free_bytes_count = len(self.main_file) - self.index_of_start_of_data
        cells_to_write_count = (free_bytes_count * 8) // self.bits_per_sample
        necessary_count_of_cells = (len(self.inserted_file) * 8) // record_unit + 64
        return cells_to_write_count >= necessary_count_of_cells

    @staticmethod
    def _define_filename(path: str):
        name = re.search(r'\\?([ _0-9а-яА-Я\w]+[^\\]\w+)?$', path).group(1)
        return bytearray(bytes(name, 'utf-8'))

    @staticmethod
    def _get_bits_per_sample(main_file):
        byte34 = main_file[34].to_bytes(1, 'little')
        byte35 = main_file[35].to_bytes(1, 'little')
        bits_per_sample = int.from_bytes(byte34 + byte35, 'little')
        return bits_per_sample

    @staticmethod
    def _create_description(list_of_pairs, bytes_to_describe_length):
        description = list(bin(len(list_of_pairs))[2:])
        while len(description) != bytes_to_describe_length:
            description = list('0') + description
        return description

    @staticmethod
    def _create_new_byte_of_flag(current_byte, description, i):
        bin_repr_current_byte = Stuff.get_bin_str_from_bytearray(current_byte)
        list_of_current_chars = list(bin_repr_current_byte)
        list_of_current_chars[-1] = description[i]
        new_byte = Stuff.get_int_from_bin(''.join(list_of_current_chars))
        return new_byte

    @staticmethod
    def _create_new_byte_of_data(current_byte, list_of_pairs, i):
        bin_repr_current_byte = Stuff.get_bin_str_from_bytearray(current_byte)
        # current_pairs = Stuff.split_in_two_bits(bin_repr_current_byte)
        current_pairs = list(bin_repr_current_byte)
        current_pairs[-1] = list_of_pairs[i]
        new_byte = Stuff.get_int_from_bin(''.join(current_pairs))
        return new_byte

    def describe_flag_and_get_index(self, bytes_to_describe, description,
                                    index, offset):
        for i in range(bytes_to_describe):  # записали информацию о длине
            current_byte = self.main_file[index: index + 1]  # вытащили байт
            new_byte = self._create_new_byte_of_flag(current_byte, description, i)
            self.main_file[index] = new_byte
            index += offset
        return index

    def describe_data_and_get_index(self, pairs, index, offset):
        for i in range(len(pairs)):  # записываем сам хеш
            current_byte = self.main_file[index: index + 1]
            new_byte = self._create_new_byte_of_data(current_byte, pairs, i)
            self.main_file[index] = new_byte
            index += offset
        return index

    def inscribe(self):
        bytes_to_describe_length_of_name = 16
        bits_of_name = Stuff.get_bin_str_from_bytearray(self.inserted_name)
        # list_of_pairs_of_name = Stuff.split_in_two_bits(bits_of_name)
        list_of_pairs_of_name = list(bits_of_name)
        name_description = self._create_description(list_of_pairs_of_name,
                                                    bytes_to_describe_length_of_name)
        bytes_to_describe_length_of_data = 32
        bits_to_write = Stuff.get_bin_str_from_bytearray(self.inserted_file)  # строка которую записываем
        # list_of_pairs_to_write = Stuff.split_in_two_bits(bits_to_write)
        list_of_pairs_to_write = list(bits_to_write)
        length_description = self._create_description(list_of_pairs_to_write,
                                                      bytes_to_describe_length_of_data)
        bytes_to_describe_length_of_hash = 8
        bits_of_hash = Stuff.get_bin_from_int(self.inserted_hash)
        # hash_pairs = Stuff.split_in_two_bits(bits_of_hash)
        hash_pairs = list(bits_of_hash)
        hash_description = self._create_description(hash_pairs,
                                                    bytes_to_describe_length_of_hash)
        offset = bytes_per_sample = self.bits_per_sample // 8
        index = self.index_of_start_of_data + bytes_per_sample
        index = self.describe_flag_and_get_index(bytes_to_describe_length_of_data,
                                                 length_description,
                                                 index, offset)
        index = self.describe_flag_and_get_index(bytes_to_describe_length_of_name,
                                                 name_description,
                                                 index, offset)
        index = self.describe_flag_and_get_index(bytes_to_describe_length_of_hash,
                                                 hash_description,
                                                 index, offset)
        index = self.describe_data_and_get_index(hash_pairs, index, offset)

        index = self.describe_data_and_get_index(list_of_pairs_of_name,
                                                 index, offset)
        self.describe_data_and_get_index(list_of_pairs_to_write,
                                         index, offset)
        with open('new_wav.wav', 'wb') as file:
            file.write(self.main_file)
