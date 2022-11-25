import os
import json
# from pprint import pprint


class Mappings:
    def __init__(self):
        self.images = {}
        self.libraries = {}

    # TODO: list of images
    # TODO: list image location: ie library or path

    def add_images(self, images):
        for (image, files) in images.items():
            image_files = []
            for file in files:
                # Gererate count of files in in libraries
                library = file['library_name']
                self.libraries[library] = self.libraries.get(library, 0) + 1

                # Cherry pick metadata to create a lean report
                image_files.append({
                    'checksum': file['checksum'],
                    'extention': file['file_extention'],
                    'library': library,
                    'path': file['file_path']
                })
            self.images[image] = image_files

    def report(self, path="reports"):
        os.makedirs(path, exist_ok=True)

        with open(os.path.join(path, 'mappings.json'), "w") as report_file:
            json.dump({
                'libraries': self.libraries,
                'images': self.images
            }, report_file)
