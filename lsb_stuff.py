class LSBStuff:
    @staticmethod
    def find_index_of_the_start_of_data(list_of_bytes: bytearray):
        offset = 8
        res = list_of_bytes.find(b'data')
        return res + offset

    @staticmethod
    def read_the_file(path_to_the_file):
        with open(path_to_the_file, 'rb') as file:
            data = bytearray(file.read())
        return data

    @staticmethod
    def get_bin_str_from_bytearray(data: bytearray):
        bin_str = ''.join('{}'.format(bin(e)[2:]) for e in data)
        while len(bin_str) % 8 != 0:
            bin_str = '0' + bin_str
        return bin_str

    @staticmethod
    def get_bin_from_int(byte):
        bin_str = bin(byte)[2:]
        while len(bin_str) % 8 != 0:
            bin_str = '0' + bin_str
        return bin_str

    @staticmethod
    def split_the_string_into_chars(string):
        return list(string)

    @staticmethod
    def split_in_two_bits(string):
        list_of_pair = []
        for i in range(len(string) // 2):
            list_of_pair.append(string[2 * i:2 * i + 2])
        return list_of_pair

    @staticmethod
    def get_int_from_bin(bin_str):
        return int(bin_str, 2)

