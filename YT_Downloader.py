from tkinter import *
from tkinter import ttk, filedialog
from tkinter.ttk import Style, Progressbar
from PIL import ImageTk, Image  # if you want to implement thumbnail
import pytube
from pytube import YouTube, Channel, exceptions
import win32clipboard
import threading
import webbrowser
import re
import sys
import os


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


root = Tk()
root.geometry('350x150')
root.resizable(width=0, height=0)
root.title('YT Downloader')

root.iconbitmap(resource_path("youtube.ico"))

filename = ''
n_name = ''
video = None
downloading = False

# ***GUI RELATED***
home_canvas = Canvas(root, bg='#808080')
home_canvas.pack(expand=True, fill='both')
about_canvas = Canvas(root, bg='#808080')

sty = Style(home_canvas)
sty.layout("LabeledProgressbar", [('LabeledProgressbar.trough',
                                   {'children': [('LabeledProgressbar.pbar',
                                                  {'side': 'left', 'sticky': 'ns'}),
                                                 ("LabeledProgressbar.label",  # label inside the bar
                                                  {"sticky": ""})],
                                    'sticky': 'nswe'})])
# PROGRESSBAR:
p_bar = Progressbar(home_canvas, orient='horizontal', length=300, mode='determinate', style='LabeledProgressbar')
p_bar.pack()
p_bar['value'] = 0
p_bar.pack_forget()

# CHANNEL LABEL:
chnl_lbl = ttk.Label(home_canvas, width=30, justify=CENTER, background='#808080', foreground='white')

# SIZE LABEL:
size_lbl = ttk.Label(home_canvas, background='#808080', foreground='white')

# DEV NAME LABEL:
name_lbl = ttk.Label(about_canvas, text='YT Downloader\nVersion 1.02\nDeveloped by: Tauhid Ahmed',
                     background='#808080', foreground='white')
name_lbl.pack(pady=(32, 0))

weblink_hyper_lbl = ttk.Label(about_canvas, foreground='white', background='#808080', text='https://www.tauhid.codes', cursor='hand1')
weblink_hyper_lbl.pack()

# IMAGE RELATED(ICONS):
github_logo_file = Image.open(resource_path("githublogo.png"))
github_link_logo = ImageTk.PhotoImage(github_logo_file)
youtube_logo_file = Image.open(resource_path("youtubelogo.png"))
youtube_link_logo = ImageTk.PhotoImage(youtube_logo_file)

# DEV GITHUB LABEL:
git_hyper_lbl = ttk.Label(about_canvas, image=github_link_logo, text='Click to get me on Github', cursor='hand1')
git_hyper_lbl.pack(side=LEFT, padx=(150, 5))

# DEV YOUTUBE LABEL:
youtube_hyper_lbl = ttk.Label(about_canvas, image=youtube_link_logo, cursor='hand1')
youtube_hyper_lbl.pack(side=LEFT)




# URL LABEL:
url_label = Label(home_canvas, width=40, justify=CENTER, bg='#808080', text="<<<Click to Paste>>>", cursor='plus',
                  fg='white')

url_label.pack(pady=15)

# MESSAGE BOX:


# BUTTONS:
dl_btn = ttk.Button(home_canvas, text='Download')
dl_btn.pack(pady=20)
about_btn = ttk.Button(home_canvas, text='About', width=6)
about_btn.pack(side=BOTTOM, pady=(0, 10), padx=(280, 10))
back_btn = ttk.Button(about_canvas, text="Back", width=5)
back_btn.place(x=10, y=10)


# ***CALLBACK FUNCTIONS***
def clear_and_paste(event):  # add event as parameter for bind method to work
    url_label.config(text="Fetching Data...")

    # get clipboard data(ctrl-c):
    win32clipboard.OpenClipboard()
    link = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()  # Close clipboard so windows can access it

    threading.Thread(target=get_info, args=[link],
                     daemon=True).start()  # Threading to show wait message while youtube data is fetched


url_label.bind("<1>", clear_and_paste)


def open_browser(url):
    webbrowser.open_new_tab(url)


weblink_hyper_lbl.bind('<Button>', lambda e: open_browser('https://www.tauhid.codes'))
youtube_hyper_lbl.bind('<Button>', lambda e: open_browser('https://www.youtube.com/channel/UCYNaebGu6N5_XoszYKVjqXA'))
git_hyper_lbl.bind("<Button>", lambda e: open_browser('https://github.com/Tauhid-Ahmed8009'))


# ***FUNCTIONS***
def get_info(link):
    global video
    global filename
    if 'https://www.youtube.com/watch' in link[0:29] and not downloading or 'https://youtu.be/' in link[
                                                                                                   0:18] and not downloading:
        try:
            dl_btn.state(['disabled'])
            yt = YouTube(link, on_progress_callback=progress)
            video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

            video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

            # Data Collection:
            size_mb = "{:.2f}".format(video.filesize * 0.000001)  # in 2 decimal places

            channel_url = yt.channel_url
            ch = Channel(channel_url)
            channel = ch.channel_name

            filename = video.default_filename

            # Labels:
            size_lbl.configure(text=f'Size: {size_mb}MB')
            size_lbl.place(x=250, y=45)
            chnl_lbl.configure(text=f'Channel: {channel}')
            chnl_lbl.place(x=20, y=45)

            url_label.config(text=filename)

            # enable the download btn
            dl_btn.state(['!disabled'])

        except pytube.exceptions.RegexMatchError:
            url_label.config(text="Video unavailable")
            dl_btn.state(['disabled'])
        except pytube.exceptions.ExtractError:
            url_label.config(text="An extraction error occurred")
            dl_btn.state(['disabled'])
        except pytube.exceptions.VideoUnavailable:
            url_label.config(text="Video unavailable")
            dl_btn.state(['disabled'])
    elif 'https://www.youtube.com/watch' in link[0:29] and downloading or 'https://youtu.be/' in link[
                                                                                                 0:18] and downloading:
        url_label.config(text="Download in progress")
        dl_btn.state(['disabled'])

    else:
        url_label.config(text="Invalid Url")
        dl_btn.state(['disabled'])


def progress(stream, chunk, bytes_remaining):
    global downloading
    size = stream.filesize
    rem = bytes_remaining
    percent = int(((size - rem) / size) * 100)
    p_bar['value'] = percent

    #  Progressbar % text using widget style:
    sty.configure("LabeledProgressbar", text="{0} %      ".format(percent))

    if percent == 100:
        sty.configure("LabeledProgressbar", text="Done          ".format(percent))
        sty.configure("LabeledProgressbar", text="".format(percent))
        p_bar.pack_forget()
        chnl_lbl.place_forget()
        size_lbl.place_forget()
        url_label.config(text='<<Click to Paste>>')
        url_label.pack(pady=15)
        about_btn.pack(side=BOTTOM, pady=(0, 10), padx=(280, 10))

        downloading = False


def download(path):
    global downloading
    dl_btn.state(['disabled'])
    downloading = True

    video.download(output_path=path, skip_existing=False,
                   filename=n_name)  # skip_existing allows overwrite of existing files


def save_file():
    global filename
    path = filedialog.asksaveasfilename(filetypes=[("mp4 file", ".mp4")], confirmoverwrite=True,
                                        defaultextension=".mp4", title='Save Location',
                                        initialfile=filename)  # save file dialog box, returns chosen path as string

    if path != "":  # cancel command returns an empty string
        #  REGEX: (to get only the directory from the path and not the filename, to avoid creation of folder)
        regex_path = re.search(r".*/", path)
        dl_path = regex_path.group(0)
        global n_name
        n_filename = re.search(r'[^/]+$', path)
        n_name = n_filename.group(0)
        about_btn.pack_forget()
        p_bar.pack()  # Making progress bar visible

        threading.Thread(target=download, args=[dl_path],
                         daemon=True).start()  # threading so that progressbar can function without UI freezing


def about():
    home_canvas.pack_forget()
    about_canvas.pack(expand=True, fill='both')


def about_exit():
    about_canvas.pack_forget()
    home_canvas.pack(expand=True, fill='both')


dl_btn.configure(command=save_file, state='disabled')
about_btn.configure(command=about)
back_btn.configure(command=about_exit)

root.mainloop()
