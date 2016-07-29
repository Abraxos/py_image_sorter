from gtk import STOCK_CANCEL # pylint: disable=E0611
from gtk import STOCK_OPEN # pylint: disable=E0611
from gtk import RESPONSE_CANCEL # pylint: disable=E0611
from gtk import RESPONSE_OK # pylint: disable=E0611
from gtk import FILE_CHOOSER_ACTION_SELECT_FOLDER # pylint: disable=E0611
from gtk import WINDOW_TOPLEVEL # pylint: disable=E0611
from gtk import POLICY_AUTOMATIC # pylint: disable=E0611
from gtk import Window # pylint: disable=E0611
from gtk import Image # pylint: disable=E0611
from gtk import ScrolledWindow # pylint: disable=E0611
from gtk import gdk # pylint: disable=E0611
from gtk import main_quit # pylint: disable=E0611
from gtk import main # pylint: disable=E0611
from gtk import FileChooserDialog # pylint: disable=E0611
from os.path import join, splitext, isfile, isdir, basename
from os import remove, walk
from shutil import copy, move
from re import compile as regex_compile

IMAGE_EXTENSIONS = set(['.png','.jpg','.jpeg','.gif','.bmp'])
REPEAT_FILE_PATT = regex_compile(r'.+\(([\d]+)\)(\..+)?')

class ImageFileEntry(object):
    def __init__(self, src_path):
        self.src_path = src_path
        self.mv_dst_path = None
        self.cp_dst_paths = []
        self.rm = False
        print("Loaded: {0}".format(self.src_path))
    def mark_mv(self, mv_dst_path):
        if isdir(mv_dst_path): mv_dst_path = join(mv_dst_path, basename(self.src_path))
        if isfile(mv_dst_path):
            m = REPEAT_FILE_PATT.match(mv_dst_path)
            filename, extension = splitext(mv_dst_path)
            if m:
                num = int(m.group(2)) + 1
                mv_dst_path = "{0}{1}){2}".format(m.group(1), num, extension)
                self.mark_mv(mv_dst_path)
            else:
                mv_dst_path = "{0} (1){1}".format(filename, extension)
                self.mark_mv(mv_dst_path)
        else:
            if mv_dst_path in self.cp_dst_paths:
                self.cp_dst_paths.remove(mv_dst_path)
            self.mv_dst_path = mv_dst_path
            print("Will move to: {0}".format(mv_dst_path))
        print(self.mv_dst_path)
    def mark_cp(self, cp_dst_path):
        if isdir(cp_dst_path): cp_dst_path = join(cp_dst_path, basename(self.src_path))
        if isfile(cp_dst_path):
            m = REPEAT_FILE_PATT.match(cp_dst_path)
            filename, extension = splitext(cp_dst_path)
            if m:
                num = int(m.group(2)) + 1
                cp_dst_path = "{0}{1}){2}".format(m.group(1), num, extension)
                self.mark_cp(cp_dst_path)
            else:
                cp_dst_path = "{0} (1){1}".format(filename, extension)
                self.mark_cp(cp_dst_path)
        elif cp_dst_path not in self.cp_dst_paths:
            self.cp_dst_paths.append(cp_dst_path)
            print("Will copy to: {0}".format(cp_dst_path))
        print(self.cp_dst_paths)
    def toggle_rm(self):
        self.rm = not self.rm
        if self.rm:
            print("Will delete: {0}".format(self.src_path))
        else:
            print("Will not delete: {0}".format(self.src_path))
    def commit(self):
        for dst in self.cp_dst_paths:
            copy(self.src_path, dst)
            print("Copied {0} to {1}".format(self.src_path, dst))
        if self.rm:
            remove(self.src_path)
            print("Deleted {0}".format(self.src_path))
        elif self.mv_dst_path:
            move(self.src_path, self.mv_dst_path)
            print("Moved {0} to {1}".format(self.src_path, self.mv_dst_path))

class ImageSortingWindow(Window):
    def __init__(self):
        super(ImageSortingWindow, self).__init__(WINDOW_TOPLEVEL)
        self.set_title('Python Image Sorter')
        self.set_size_request(800,600)

        self.src_dir = None
        self.entries = []
        self.destinations = {}

        self.image = Image()
        self.image.connect('expose-event', self.on_image_resize)
        self.pixbuf = None
        self.temp_w, self.temp_h = None, None

        self.box = ScrolledWindow()
        self.box.set_policy(POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        self.box.add(self.image)
        self.add(self.box)
        self.connect('key_press_event', self.on_key_function)

        self.src_dir = self.directory_prompt()

        if not self.src_dir: exit()

        self.load_images()

        if not self.entries: exit()
        self.show_all()

    def load_images(self):
        self.image_index = 0
        self.temp_w = 0
        self.temp_h = 0
        self.entries = []
        # self.entries = sorted([ImageFileEntry(join(self.src_dir, f)) for f in listdir(self.src_dir) if splitext(f)[1] in IMAGE_EXTENSIONS])
        for root, _, files in walk(self.src_dir):
            for f in files:
                if splitext(f)[1] in IMAGE_EXTENSIONS:
                    self.entries.append(ImageFileEntry(join(root, f)))
        self.entries.sort()
        if self.entries:
            self.update_image()

    def commit(self):
        for entry in self.entries:
            entry.commit()
        self.load_images()
        if not self.entries:
            exit()

    def process_key(self, keyname):
        if keyname.isalpha() and len(keyname) == 1:
            if keyname not in self.destinations:
                d = self.directory_prompt(title="Please select a directory to associate with: [{0}]".format(keyname))
                if not d: return
                self.destinations[keyname.title()] = d
                self.destinations[keyname.lower()] = d
            entry = self.entries[self.image_index]
            if keyname.istitle():
                entry.mark_cp(self.destinations[keyname])
            else:
                entry.mark_mv(self.destinations[keyname])
                self.next_image()

    def delete(self):
        self.entries[self.image_index].toggle_rm()
        self.next_image()

    def on_key_function(self, widget, event): # pylint: disable=W0613
        keyname = gdk.keyval_name(event.keyval)
        print("Key %s (%d) was pressed" % (keyname, event.keyval))

        if keyname == 'Right':
            self.next_image()
        elif keyname == 'Left':
            self.prev_image()
        elif keyname == 'Return':
            self.commit()
        elif keyname == "Delete":
            self.delete()
        else:
            self.process_key(keyname)

    def on_image_resize(self, widget, event): # pylint: disable=W0613
        self.scale_to_fit()

    def scale_to_fit(self, force=False):
        image_size = (self.pixbuf.get_width(), self.pixbuf.get_height())
        allocation = self.box.get_allocation()
        allocation_size = (allocation.width, allocation.height)
        if force or allocation_size[0] != self.temp_w or allocation_size[1] != self.temp_h:
            self.temp_w = allocation_size[0]
            self.temp_h = allocation_size[1]
            width_scale = float(allocation_size[0]) / float(image_size[0])
            height_scale = float(allocation_size[1]) / float(image_size[1])
            s = min(width_scale, height_scale)
            w = int(image_size[0] * s)
            h = int(image_size[1] * s)

            pixbuf = self.pixbuf.scale_simple(w-1, h-1, gdk.INTERP_BILINEAR)
            self.image.set_from_pixbuf(pixbuf)

    def update_image(self):
        filename = self.entries[self.image_index].src_path
        self.set_title('Python Image Sorter: ' + filename)
        self.pixbuf = gdk.pixbuf_new_from_file(filename)
        self.image.set_from_pixbuf(self.pixbuf)
        self.scale_to_fit(force=True)

    def next_image(self):
        if self.image_index < len(self.entries) - 1:
            self.image_index += 1
            self.update_image()

    def prev_image(self):
        if self.image_index > 0:
            self.image_index -= 1
            self.update_image()

    def close_application(self, widget, event, data=None): # pylint: disable=W0613
        main_quit()
        return False

    def directory_prompt(self, title="Please choose a folder"):
        dialog = FileChooserDialog(title, self,
            FILE_CHOOSER_ACTION_SELECT_FOLDER,
            (STOCK_CANCEL,RESPONSE_CANCEL,
             STOCK_OPEN,
             RESPONSE_OK))
        dialog.set_default_size(800, 400)

        response = dialog.run()
        if response == RESPONSE_OK:
            print("Select clicked")
            print("Folder selected: " + dialog.get_filename())
            directory = dialog.get_filename()

            dialog.destroy()
            return directory

        dialog.destroy()
        return False

if __name__ == "__main__":
    image_sorter = ImageSortingWindow()
    if image_sorter:
        image_sorter.connect("delete-event", main_quit)
        main()
