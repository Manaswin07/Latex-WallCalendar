import glob
import pathlib
from datetime import date
import sys
import pandas as pd
from tkinter import Label
from tkinter import StringVar
from tkinter import Entry
from tkinter import Button
from tkinter import filedialog
from tkinter import Tk
import calendar
import tempfile
import os
try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = sys._MEIPASS
except Exception:
    base_path = os.path.abspath(".")
HEAD = base_path+"/head.txt"

debug = False

class LatexCalendar(calendar.Calendar):

    def __init__(self, tempdir, *args):
        super(calendar.Calendar, self)

        # set year
        self.year = int(args[0])
        self.titlephotos = args[-1][:12]
        self.footnotephoto = args[-1][-1]
        # setup csv data
        if len(args) > 1:
            self.parse_file(args[1])
        else:
            self.data = None

        # configure calendar
        if len(args) > 3:
            self.setfirstweekday(int(args[2]))
        else:
            self.setfirstweekday(0)

        # helper stuff
        self.texfile =open(os.path.join('../','texfile'),'w')#tempfile.NamedTemporaryFile(dir=tempdir, mode='w', delete=False)
        self.heights = [0] * 7
        self.heights[4] = 0
        self.heights[5] = 0
        self.heights[6] = 0
        self.sun_index = [ x for x in self.iterweekdays() ].index(6)

    def parse_file(self, filename):

        self.data = dict()
        for i in range(1, 13):
            self.data[i]=dict()

        with open(filename) as datafile:
            first = True
            for line in datafile:
                if first:
                    first = False
                    continue
                #print(line)
                ind,date,name=line.strip().split(',')
                special = 0
                d,m,_ = map(int, date.split('/'))

                if (m in self.data.keys() and d in self.data[m].keys()):
                    self.data[m][d].append((name, special))
                else:
                    self.data[m][d] = [(name, special)]

    @property
    def has_bdays(self):
        return self.data is not None

    def generate_file(self):
        # add header to texfile
        with open(HEAD, "r") as header:
            for line in header:
                self.texfile.write(line.replace("%year%", str(self.year)))

        # add months 1 - 12
        for month in range(1,13):
            # get additional data for this month
            if self.has_bdays:
                monthdata = self.data[month]
            else:
                monthdata = dict()

            # table header
            self.texfile.write("\\begin{calmonth}{%s}{%d}{%s}\n\hline\n" % (calendar.month_name[month], self.year,self.titlephotos[month-1]))
            # table header: day names
            days = [d[0:2] for d in calendar.day_abbr]
            days[self.sun_index] = "\\textcolor{socol}{%s}" % days[self.sun_index]
            self.texfile.write("&".join(days))
            self.texfile.write("\\\\\n\hline\n")

            # generate day entries
            mdays = self.monthdayscalendar(self.year, month)
            lines = []
            for l in mdays:
                sunday_done = False
                last_day_in_week = False
                # insert special data
                line = list(l)
                for (day, datas) in monthdata.items():
                    try:
                        i = l.index(day)
                    except ValueError:
                        continue
                    if i != -1:
                        # add day number
                        if i == self.sun_index:
                            # color sundays red
                            line[i] = "\\textcolor{socol}{%s}" % l[i]
                            sunday_done=True
                        else:
                            line[i] = str(l[i])

                        # TODO: refactor + move latex magic into macros
                        # process extra data
                        if len(datas) == 1:
                            data = datas[0]
                            if data[1] != "":
                                line[i] = line[i] + "\\newline {\\raggedright\\normalsize\\textcolor{special}{%s}}" % (data[0])
                            else:
                                line[i] = line[i] + "\\newline {\\raggedright\\normalsize %s}" % (data[0])
                        elif len(datas) > 1:
                            line[i] = line[
                                          i] + "\\newline {\\raggedright\\normalsize "
                            for data in datas:
                                if data[1] != "":
                                    line[i] = line[i] + " \\textcolor{special}{%s}\\newline" % (data[0])
                                else:
                                    line[i] = line[i] + "{%s}\\newline" % (data[0])
                            line[i] = line[i] + " }"

                    if i == 6:
                        last_day_in_week = True

                if not sunday_done:
                    # color sundays red
                    if line[self.sun_index] != 0:
                        line[self.sun_index] = "\\textcolor{socol}{%s}" % line[self.sun_index]


                # output is more complicated when last day in week has additional data
                lines.append(("&".join([str(y) if y != 0 else "" for y in line]), last_day_in_week))

            height = self.heights[len(lines)]

            # output
            for line,last_day_in_week in lines:
                if last_day_in_week:
                    h = height
                else:
                    h = height
                self.texfile.write("%s\\\\[%.1fcm]\n\hline\n"%(line,h))
            #self.texfile.write(("\\\\[%.1fcm]\n\hline\n"%height).join(lines))
            #self.texfile.write("\\\\[%.1fcm]\n\hline\n"%height)
            self.texfile.write("\\end{calmonth}\n \\ \lastimage{%s} \\ \n"% (self.footnotephoto))

        self.texfile.write("\end{document}\n\n")
        self.texfile.flush()
        # file = open('output.tex', 'w+')
        # file.write(self.texfile)
        # file.close()


    def pdflatex(self, outprefix="cal"):
        import subprocess
        ret = subprocess.call(["pdflatex", self.texfile.name],stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL) #
        if not debug and ret == 0:
            fname = os.path.basename(self.texfile.name)
            #print(fname)
            try:
                os.remove(os.path.join('../',"%s_%d.pdf" % (outprefix, self.year)))
            except:
                pass
            self.texfile.close()
            os.remove(fname + ".aux")
            os.remove(fname + ".log")
            os.remove('tempinput.csv')
            os.rename(fname + ".pdf", os.path.join('../',"%s_%d.pdf" % (outprefix, self.year)))
            os.remove(os.path.abspath(self.texfile.name))


# def usage(*args):
#     print("usage: {} <year> [csv-data [first-day-of-week]]".format(args[0][0]))
#     print()
#     print("   where first-day-of-week is one of 0=Monday, ..., 6=Sunday")
#     print()

# arguments: year, csv-data, weekstart
def calfunc(year,imgs,csvloc=None):
    try:
    # set locale: used for generating month and day names
        import locale
        import os
        import sys
        locale.setlocale(locale.LC_ALL, '')
        locale.setlocale(locale.LC_TIME, '')

        outprefix = "cal"
        if csvloc!=None:
            outprefix, _ = os.path.splitext(os.path.basename(csvloc))

        pc = LatexCalendar(os.path.dirname(sys.argv[0]), *[year,csvloc,imgs])
        pc.generate_file()
        pc.pdflatex(outprefix="calendar")
        return 0
    except Exception as e:
        print(e)
        return -5

# calfunc(2021,'../jk3.csv',imgs)

class MyWindow:
    def __init__(self, win):
        self.row_pos = [100,150,250]
        self.col_pos = [100,200,300]
        self.lbl1=Label(win, text='Calendar Year')
        self.lbl2=Label(win, text='Datafile (.csv)')
        self.lbl3=Label(win, text='Image Folder')
        self.lbl4 = Label(win,text='Calendar Maker',font=("Helvetica",24))
        self.folderPath = StringVar()
        self.showyear = StringVar()
        self.showyear.set(str(date.today().year))
        self.folderPath.set('../Images')
        self.csvPath = StringVar()
        self.csvPath.set('../TestInput.csv')
        self.t1=Entry(text=self.showyear)
        self.t2=Entry(text=self.csvPath)
        self.t3=Entry(text=self.folderPath)
        self.b2 = Button(win, text='Browse', command=self.getFilePath)
        self.b1 = Button(win, text='Create Calendar', command= self.entryfl)
        self.b3 = Button(win, text='Browse', command=self.getFolderPath)
        self.lbl1.place(x=100, y=100)
        self.t1.place(x=200, y=100)
        self.b1.place(x=200, y=250)
        self.lbl2.place(x=100, y=150)
        self.t2.place(x=200, y=150)
        self.b2.place(x=375, y=145)
        self.lbl3.place(x=100, y=200)
        self.t3.place(x=200, y=200)
        self.b3.place(x=375, y=195)
        self.lbl4.place(x=130, y=20)
        self.status_label = StringVar()
        self.lbl5 = Entry(win,text=self.status_label,justify='center')
        self.status_label.set("Press Create Calendar to generate your calendar")
        self.lbl5.place(x=0,y=350,width = 500)
    def getFolderPath(self):
        folder_selected = filedialog.askdirectory()
        self.folderPath.set(folder_selected)
    def getFilePath(self):
        file_selected = filedialog.askopenfilename()
        self.csvPath.set(file_selected)
    def entryfl(self):
        new_data_column = []
        date = []
        df = pd.read_csv(self.csvPath.get())
        col_entries = list(df.columns)[1:]
        for j in df.index:
            for i in range(1, len(col_entries)):
                # date.append(df['Date'][j])
                new_data_column.append((df['Date'][j], col_entries[i] + ': ' + df[col_entries[i]][j]))
            new_df = pd.DataFrame(new_data_column, columns=['Date', 'Info'])
            new_df.to_csv('tempinput.csv')
        months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','Footer']
        image_list =[]

        for i in months:
            image_list = image_list+ glob.glob(self.folderPath.get()+"/%s.*" % i)
        #image_list = [glob.glob(self.folderPath.get()+"/%s.*" % i) for i in months ]#+glob.glob(imageloc+"/*.jpg")+glob.glob(imageloc+"/*.png")
        if len(image_list)==13:
            image_list = image_list
        elif len(image_list)==2:
            image_list = [image_list[0]]*12+[image_list[-1]]
        else:
            self.status_label.set('ERROR: Incorrect Number of Photos In Folder')
        #image_list.sort()
        for i in range(len(image_list)):
            pa = pathlib.PureWindowsPath(image_list[i])
            image_list[i] = str(pa.as_posix())
        # print('Please enter the year for which to generate the calendar (e.g 2020,2021,etc...)')
        # year = input()
        retstatus = calfunc(int(self.t1.get()),image_list,'tempinput.csv')
        if retstatus==0:
            self.status_label.set("Successfully generated %s_%d.pdf. Close window to exit." % ('calendar', int(self.t1.get())))
        else:
            self.status_label.set("Failed to generate file, errors occured")

window=Tk()
mywin=MyWindow(window)
window.title('Calendar Maker')
window.geometry("500x400+1200+100")
window.mainloop()