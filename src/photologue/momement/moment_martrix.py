from typing import Any, Callable
import logging

Matrix = list[list[list[dict[str, Any]]]]


class Moment_Matrix():

    def __init__(self, files: list[dict]):
        self.LOGGER = logging.getLogger('Moment_Matrix')
        self.idx_image: list = []
        self.idx_checksum: list = []
        self.matrix: Matrix = []
        self.__generate(files)

    def __generate(self, files: list) -> None:
        # Create a marrix with dimentions: image name, checksums
        for file in files:
            image = file['file_name']
            if image not in self.idx_image:
                self.idx_image.append(image)
            i = self.idx_image.index(image)

            checksum = file['checksum']
            if checksum not in self.idx_checksum:
                self.idx_checksum.append(checksum)
            c = self.idx_checksum.index(checksum)

            # Recreate matrix for additional dimentions
            if len(self.idx_image) > len(self.matrix) or len(self.idx_checksum) > len(self.matrix[0]):
                new_matrix: list[list[list[dict]]] = [
                    [
                        [] for x in range(len(self.idx_checksum))
                    ] for y in range(len(self.idx_image))
                ]
                # copy existing matrix to new matrix
                for x in range(len(self.matrix)):
                    for y in range(len(self.matrix[0])):
                        new_matrix[x][y] = self.matrix[x][y]

                self.matrix = new_matrix

            self.matrix[i][c].append(file)

    def shape(self) -> None:
        print("shape")
        for row in self.matrix:
            name = ''
            counts = []
            for checksum in row:
                counts.append(len(checksum))
                if len(checksum) > 0 and not name:
                    file = checksum[0]
                    name = file['file_name']

            if not name:
                name = 'REMOVED ->'

            print(f"\t{name}\t", counts)

    def files(self) -> list:
        files: list = []
        for row in self.matrix:
            for column in row:
                files = [*files, *column]
        return files

    # def list_matrix_files(self, group: str) -> None:
    #     list_files(group, self.files())

    # TODO: Size of rows, size of columns

    def images(self) -> list[str]:
        return self.idx_image

    def checksums(self) -> list[str]:
        return self.idx_checksum

    def m(self, image: str, checksum: str) -> list[dict]:
        i = self.idx_image.index(image)
        j = self.idx_checksum.index(checksum)

        return self.matrix[i][j]

    def empty_matrix(self) -> Matrix:
        return [
            [
                [] for c in range(len(self.matrix[0]))
            ] for r in range(len(self.matrix))
        ]

    # TODO: Write a test for this!
    def ignore(self, ignoreFn: Callable, ignore_rules) -> list[dict]:
        ignored_files: list[dict] = []

        filtered_matrix: Matrix = self.empty_matrix()
        # extentions = set()

        # Filter out ignored images
        for row in range(len(self.matrix)):
            for column in range(len(self.matrix[row])):
                filtered = []
                for file in self.matrix[row][column]:
                    if ignoreFn(ignore_rules, file['file_path']):
                        ignored_files.append(file)
                        continue
                    # extentions.add(file['file_extention'])
                    filtered.append(file)
                filtered_matrix[row][column] = filtered

        # Clean up matrix where ignored files leave empty rows or columns
        self.cleanup(filtered_matrix)
        return ignored_files

    def filter(self, filterFor: Callable, filter_rules) -> list[dict]:
        filtered_files: list[dict] = []
        filtered_matrix: Matrix = self.empty_matrix()

        for row in range(len(self.matrix)):
            for column in range(len(self.matrix[row])):
                filtered = []
                for file in self.matrix[row][column]:
                    # TODO: Filter
                    if filterFor(filter_rules, file):
                        filtered.append(file)
                        # print('Keep', file['file_path'])
                    else:
                        # print('Ignore', file['file_path'])
                        filtered_files.append(file)
                filtered_matrix[row][column] = filtered

        if not len(filtered_matrix):
            # TODO Deal with an empty matrix
            # print("EMPTY Matrix - Not updated !!!")
            pass
        # Clean up matrix where filtered files leave empty rows or columns
        else:
            self.cleanup(filtered_matrix)
        return filtered_files

    # TODO: Write a test for this!
    def cleanup(self, filtered_matrix) -> None:
        # Create new indexes
        new_idx_images = []
        new_idx_checksums = []
        empty_checksums = [True for c in range(len(filtered_matrix[0]))]
        cleaned_images: Matrix = []
        cleaned_matrix: Matrix = []
        row_count = len(filtered_matrix)

        # Locate empty coloumns and drop empty rows
        for image in range(row_count):
            image_empty = True
            image_name = ''
            for checksum in range(len(filtered_matrix[image])):
                if len(filtered_matrix[image][checksum]) > 0:
                    # There are files at this vertice
                    file = filtered_matrix[image][checksum][0]
                    image_name = file['file_name']
                    image_empty = False
                    empty_checksums[checksum] = False
            if not image_empty:
                cleaned_images.append(filtered_matrix[image])
                new_idx_images.append(image_name)
            # else discard if row is empty

        # Check for empty columns
        for cleaned_row in cleaned_images:
            cleaned_columns: list[list[dict]] = []

            for col_pos in range(len(cleaned_row)):
                column = cleaned_row[col_pos]
                checksum = 0
                if len(column):
                    file = column[0]
                    checksum = file['checksum']
                if not empty_checksums[col_pos]:
                    if checksum not in new_idx_checksums:
                        new_idx_checksums.append(checksum)
                    cleaned_columns.append(column)
            cleaned_matrix.append(cleaned_columns)

        self.idx_checksum = new_idx_checksums
        self.idx_image = new_idx_images
        self.matrix = cleaned_matrix
        # TODO Deal with an empty matrix


def show_shape(m) -> None:
    for row in m:
        name = ''
        counts = []
        for checksum in row:
            counts.append(len(checksum))
            if len(checksum) > 0 and not name:
                file = checksum[0]
                name = file['file_name']

        if not name:
            name = 'REMOVED ->'

        print(f"\t{name}\t", counts)
