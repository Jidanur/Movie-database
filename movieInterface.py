from codeop import CommandCompiler
import sqlite3
from tkinter import *
import tkinter as tk
from tkinter import Tk, ttk
from tkinter.messagebox import showinfo
from tabulate import tabulate

tabulate.PRESERVE_WHITESPACE = True


#function for exporting results in CSV file
def exportCSV():
    contents = ""
    out = open("export.csv","w",encoding="utf-8")
    for r in range(len(export_list)):
        for c in range(len(export_list[r])):
            contents += str(export_list[r][c]) + ","
        contents +="\n"
        
    out.write(contents)
    out.close()

    showinfo("DONE","Results succesfully exported to export.csv")



def resetCombos():
    MovieName.set('')
    prod_cb.set('')
    year_cb.set('')
    contries_cb.set('')
    genre_selected.set('')

def searchMovie():
    #used for debug purpose
    msg = f"name: {MovieName.get()} \nyear: {select_year.get()} \nproductionCOMP:{producedBy.get()} \ncountry:{productionCountry.get()}"
    

    # run the sql command on the database and store it in a list
    sql_cmd = f"""SELECT title, release_date, budget, revenue, prodCompany.name as productionCompany, prodCountry.name as countryOfProduction, Genre.name as Genre from movie 
        join prodCompany on prodCompany.id = movie.id
        join prodCountry on prodCountry.id = movie.id
        join Genre on Genre.id = movie.id
        where title like '{MovieName.get()}%' and
        release_date like '%{select_year.get()}' and
        prodCompany.name like '{producedBy.get()}%' and
        prodCountry.name like '{productionCountry.get()}%' and
        Genre.name like '{genre_selected.get()}%'
        group by movie.id
        """

    results_q = db.execute(sql_cmd)
    results_list = list(results_q)
    headings = [col[0]  for col in results_q.description]
    results_list.insert(0,headings)

    # if no data found for the inteded query then 
    if len(results_list) < 2:
        showinfo("Sorry","No data exists for the search results")
        return


    #set current list to export
    global export_list 
    export_list = results_list

    #intialize result window
    resultWindow = Tk()
    resultWindow.title("Search results")
    resultWindow.geometry("1280x720")

     # Create a menu bar
    menu_bar = tk.Menu(resultWindow)
    resultWindow.config(menu=menu_bar)

    # Create options menu
    options_menu = tk.Menu(menu_bar)
    menu_bar.add_cascade(label="Options", menu=options_menu)
    options_menu.add_command(label="Export as CSV", command=exportCSV)
    

    frame_box = ttk.Frame(resultWindow)
    frame_box.grid(row=0, column=0, sticky='nsew')

    #grid config for the frame
    frame_box.grid_columnconfigure(0,weight=1)
    frame_box.grid_rowconfigure(0,weight=1)
    

    #tree view for the result data
    #adjusting tree to frame_box
    tree = ttk.Treeview(frame_box)
    tree.grid(row=0, column=0, sticky='nsew')


    # creating headings 
    tree['columns'] = [str(x) for x in range(len(results_list[0]))]
    tree.column("#0", width=70, minwidth=70, stretch=tk.NO)

    for i in range(len(results_list[0])):
        tree.column(str(i), width=150, minwidth=150, stretch=tk.NO)
        tree.heading(str(i), text=results_list[0][i], anchor=tk.W)
    
    for i in tree.get_children():
        tree.delete(i)

    for row in results_list[1:]:
        tree.insert("","end",values=row)


    yScrollbar = ttk.Scrollbar(frame_box,orient='vertical')
    yScrollbar.grid(row=0,column=1,sticky='ns')
    tree['yscrollcommand']= yScrollbar.set
    yScrollbar.config(command=tree.yview)


    resultWindow.columnconfigure(0, weight=1)
    resultWindow.rowconfigure(0, weight=1)
    
    
    resultWindow.mainloop()



    


db = sqlite3.connect("movieDB.db")  #movie database to access our query

#getting all prod company ordered by total movies produced
prod_companies = db.execute("SELECT pid,name from prodCompany GROUP by pid ORDER by count(id) DESC")

#getting all contries movie was produced ordered by total movies count
contries_list = db.execute("SELECT cd,name from prodCountry GROUP by cd ORDER by count(id) DESC")


#genres exists in the database ordered by most movies
genre_list = db.execute("SELECT gid,name from Genre GROUP by gid ORDER by count(id) DESC")

#production years
year_list = [x for x in range(1900,2019)]

#global variable used for exporting the resulted list
export_list = []


#MAIN UI
root = tk.Tk()
root.title("Movie Database")
root.geometry('790x648')

ico = tk.PhotoImage(file= 'icon.png')
root.iconphoto(False,ico)


MovieName = tk.StringVar()

# search box frame
searchFrame = tk.Frame(root)
searchFrame.columnconfigure(0,weight=8)
searchFrame.rowconfigure(0,weight=3)

searchFrame.pack(padx= 10,pady= 10,fill='x', expand=True)


# search entry
search_label = tk.Label(searchFrame, text="Search by Movie Name:")
search_label.grid(column=0,row=0,sticky=tk.EW,columnspan=8)

search_entry = tk.Entry(searchFrame, textvariable=MovieName)
search_entry.grid(column=0,row=1,sticky=tk.EW,columnspan=8)

search_entry.focus()



#prod company select
prod_label = tk.Label(searchFrame, text="Produced By:")
prod_label.grid(column=0,row=2,sticky=tk.W)

producedBy = tk.StringVar()
prod_cb = ttk.Combobox(searchFrame,textvariable=producedBy)

prod_cb["values"] = [p[1] for p in prod_companies]
prod_cb["state"] = "readonly"

prod_cb.grid(column=1,row=2,sticky=tk.W)

#country select
country_label = tk.Label(searchFrame, text="Country:")
country_label.grid(column=2,row=2,sticky=tk.W)

productionCountry = tk.StringVar()
contries_cb = ttk.Combobox(searchFrame,textvariable=productionCountry)

contries_cb["values"] = [p[1] for p in contries_list]
contries_cb["state"] = "readonly"

contries_cb.grid(column=3,row=2,sticky=tk.W)

#genre select
genre_label = tk.Label(searchFrame, text="Genre:")
genre_label.grid(column=4,row=2,sticky=tk.W)

genre_selected = tk.StringVar()
genre_cb = ttk.Combobox(searchFrame,textvariable=genre_selected)

genre_cb["values"] = [p[1] for p in genre_list]
genre_cb["state"] = "readonly"

genre_cb.grid(column=5,row=2,sticky=tk.W)


#year select
year_label = tk.Label(searchFrame, text="Year:")
year_label.grid(column=6,row=2,sticky=tk.W)

select_year = tk.StringVar()
year_cb = ttk.Combobox(searchFrame,textvariable=select_year)

year_cb["values"] = [y for y in year_list]
year_cb["state"] = "readonly"

year_cb.grid(column=7,row=2,sticky=tk.W)


# Search button
search_ico = tk.PhotoImage(file= 'lookup_ico.png')
search_button = tk.Button(searchFrame,  text="Search" ,command=searchMovie,fg="Blue",image=search_ico)

search_button.grid(column= 3,row=3,sticky=tk.W,pady=10)
search_button.focus()

# clear button
clear_button = tk.Button(searchFrame,  text="Clear" ,command=resetCombos,fg="Red",font="bold")
clear_button.grid(column= 3,row=3,sticky=tk.E,columnspan=1)
clear_button.focus()


root.mainloop()
