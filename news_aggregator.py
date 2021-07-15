#-----Statement of Authorship----------------------------------------#
#
#  This was written by Jack Gate-Leven and submitted to QUT for an 
#  assignment. Import statements 
#
#--------------------------------------------------------------------#



#-----Description----------------------------------------------------#
#
#  News Feed Aggregator
#
#  Using a combination of skills in HTMl/XML mark-up languages and
#  Python scripting, pattern matching, and Graphical User Interface
#  design, I will produce an application that allows the user to
#  aggregate RSS news feeds. Users can create a custom selection of
#  news articles to look at on a personal webpage.
#--------------------------------------------------------------------#



#-----Imported Functions - QUT content-------------------------------#

# Import the standard Tkinter functions. (You WILL need to use
# these functions in your solution.  You may import other widgets
# from the Tkinter module provided they are ones that come bundled
# with a standard Python 3 implementation and don't have to
# be downloaded and installed separately.)
from tkinter import *

# Import a special Tkinter widget we used in our demo
# solution.  (You do NOT need to use this particular widget
# in your solution.  You may import other such widgets from the
# Tkinter module provided they are ones that come bundled
# with a standard Python 3 implementation and don't have to
# be downloaded and installed separately.)
from tkinter.scrolledtext import ScrolledText

# Functions for finding all occurrences of a pattern
# defined via a regular expression, as well as
# the "multiline" and "dotall" flags.  (You do NOT need to
# use these functions in your solution, because the problem
# can be solved with the string "find" function, but it will
# be difficult to produce a concise and robust solution
# without using regular expressions.)
from re import findall, finditer, MULTILINE, DOTALL

# Import the standard SQLite functions (just in case they're
# needed one day).
from sqlite3 import *

#--------------------------------------------------------------------#



#---------QUT content------------------------------------------------#

# A function to download and save a web document. If the
# attempted download fails, an error message is written to
# the shell window and the special value None is returned.
#
# Parameters:
# * url - The address of the web page you want to download.
# * target_filename - Name of the file to be saved (if any).
# * filename_extension - Extension for the target file, usually
#      "html" for an HTML document or "xhtml" for an XML
#      document or RSS Feed.
# * save_file - A file is saved only if this is True. WARNING:
#      The function will silently overwrite the target file
#      if it already exists!
# * char_set - The character set used by the web page, which is
#      usually Unicode UTF-8, although some web pages use other
#      character sets.
# * lying - If True the Python function will hide its identity
#      from the web server. This can be used to prevent the
#      server from blocking access to Python programs. However
#      we do NOT encourage using this option as it is both
#      unreliable and unethical!
# * got_the_message - Set this to True once you've absorbed the
#      message about Internet ethics.
#
def download(url, target_filename, filename_extension, save_file,
             char_set, lying, got_the_message):

    # Import the function for opening online documents and
    # the class for creating requests
    from urllib.request import urlopen, Request

    # Import an exception raised when a web server denies access
    # to a document
    from urllib.error import HTTPError

    # Open the web document for reading
    try:
        if lying:
            # Pretend to be something other than a Python
            # script (NOT RECOMMENDED!)
            request = Request(url)
            request.add_header('User-Agent', 'Mozilla/5.0')
            #if not got_the_message:
                #print("Warning - Request does not reveal client's true identity.")
                #print("          This is both unreliable and unethical!")
                #print("          Proceed at your own risk!\n")
        else:
            # Behave ethically
            request = url
        web_page = urlopen(request)
    except ValueError:
        print("Download error - Cannot find document at URL '" + url + "'\n")
        return None
    except HTTPError:
        print("Download error - Access denied to document at URL '" + url + "'\n")
        return None
    except Exception as message:
        print("Download error - Something went wrong when trying to download " + \
              "the document at URL '" + url + "'")
        print("Error message was:", message, "\n")
        return None

    # Read the contents as a character string
    try:
        web_page_contents = web_page.read().decode(char_set)
    except UnicodeDecodeError:
        print("Download error - Unable to decode document from URL '" + \
              url + "' as '" + char_set + "' characters\n")
        return None
    except Exception as message:
        print("Download error - Something went wrong when trying to decode " + \
              "the document from URL '" + url + "'")
        print("Error message was:", message, "\n")
        return None

    # Optionally write the contents to a local text file
    # (overwriting the file if it already exists!)
    if save_file:
        try:
            text_file = open(target_filename + '.' + filename_extension,
                             'w', encoding = char_set)
            text_file.write(web_page_contents)
            text_file.close()
        except Exception as message:
            print("Download error - Unable to write to file '" + \
                  target_filename + "'")
            print("Error message was:", message, "\n")

    # Return the downloaded document to the caller
    return web_page_contents

#--------------------------------------------------------------------#



#-----Jack Gate-Leven work-------------------------------------------#
#
# Put your solution at the end of this file.
#

# Name of the exported news file. To simplify marking, your program
# should produce its results using this file name.
news_file_name = 'news.html'

### Create database connection
connection = connect(database = "news_log.db")

# Get a pointer into the database
news_log_db = connection.cursor()

### Function that gets articles from sources ready for use
def update_news_info():

    ### Getting the archived news files ready
    # Getting Wired file
    wired_feed = open('wired_9_13.xml') # Open the wired file
    wired_text = wired_feed.read()
    wired_feed.close() # Close the wired file

    # Getting Quensland Times file 
    qt_feed = open('qt_16_9.xml', encoding="utf8") # Open the qt file
    qt_text = qt_feed.read()
    qt_feed.close() # Close the qt file

    ### Downloading the live news feeds
    # Canberra Times download of news feed
    canberra_text = download('https://www.canberratimes.com.au/rss.xml'
                                   ,'Canberra Times','xhtml',False,'UTF-8',True,False)

    # Goulburn download of news feed
    goulburn_text = download('https://www.goulburnpost.com.au/rss.xml'
                                   ,'Goulburn Post','xhtml',False,'UTF-8',True,False)

    ### Breaking text down into different stories then into information stored within
    scrape_articles(wired_text,qt_text,canberra_text,goulburn_text)
    

# Using article text to get required info and articles 
def scrape_articles(wired_text,qt_text,canberra_text,goulburn_text):

    ### Seperate news feeds into their seperate article segments
    # number of articles per news site to use
    articles_to_load = 10

    # Defining lists to hold articles
    wr_articles = []
    qt_articles = []
    cb_articles = []
    gl_articles = []
    
    # Wired article splitting
    wr_articles = wr_articles + findall(r'<item>.*?</item>',wired_text)
    # Split the list to required article length
    # The Slice is used to cut the opening advert section from the article list
    wr_articles = wr_articles[1:1+articles_to_load]
    
    # qt article splitting
    qt_articles = qt_articles + findall(r'<item>.*?</item>',qt_text, DOTALL)
    # Split the list to required article length
    qt_articles = qt_articles[:articles_to_load]

    # Canberra Times article splitting
    cb_articles = cb_articles + findall(r'<item>.*?</item>',canberra_text, DOTALL)
    # Split the list to required article length
    cb_articles = cb_articles[:articles_to_load]

    # Goulburn article splitting
    gl_articles = gl_articles + findall(r'<item>.*?</item>',goulburn_text, DOTALL)
    # Split the list to required article length
    gl_articles = gl_articles[:articles_to_load]
    
    ### Function to seperate articles in information segments ie title, date
    def seperate(articles_list,segment_list):
        for article in (articles_list):
            # Setting regex statements before execution to neaten code
            title_find = r'<title>(.*?)</title>'
            image_find_1 = r'<media:thumbnail url="(.*?)"'
            image_find_2 = r'<media:thumbnail url="(.*?)"'
            image_find_3 = r'<enclosure url="(.*?)"'
            description_find = r'<description>(.*?)</description>'
            link_find = r'<link>(.*?)</link>'
            date_find = r'<pubDate>(.*?)</pubDate>'
            

            ### Searching for all segments needed
            current_text = []
            
            # Getting article Title
            current_text = current_text + findall(title_find,article, DOTALL)

            # Getting article img
            if "media:content" in article:
                current_text = current_text + findall(image_find_1,article, DOTALL) 

            elif "media:thumbnail" in article:
                current_text = current_text + findall(image_find_2,article, DOTALL)

            elif "enclosure url" in article:
                current_text = current_text + findall(image_find_3,article, DOTALL)            

            # Getting article summary
            current_text = current_text + findall(description_find,article, DOTALL)
            
            # Getting article link
            current_text = current_text + findall(link_find,article, DOTALL)

            # Getting article publication date
            current_text = current_text + findall(date_find,article, DOTALL)

            
            #add list with the articles segments to a list of all the articles
            segment_list.append(current_text)
        
    ### Collecting article's contents in order (Title, img link, Summary, link, Publication date)
    # Setting lists for use
    wr_segments = []
    qt_segments = []
    cb_segments = []
    gl_segments = []
    
    # Split all article sets into segments
    seperate(wr_articles,wr_segments)
    seperate(qt_articles,qt_segments)
    seperate(cb_articles,cb_segments)
    seperate(gl_articles,gl_segments)

    # Call GUI program to start using segment lists
    gui_program(wr_segments,qt_segments,cb_segments,gl_segments)
    

### Create the GUI using Tkinter
def gui_program(wr_segments,qt_segments,cb_segments,gl_segments):

    ### Program for when export button is clicked
    def export_stories():
        # Create html file using selected number of stories
        html_create(wr_segments,qt_segments,cb_segments,gl_segments,wr_spinbox.get(),
        qt_spinbox.get(),cb_spinbox.get(),0,0)

        # Close GUI after export button is clicked
        window.destroy()

    ### Change when spinbox is used to update story summaries
    def spinbox_change():
        summary_text.delete('1.0',END) # Clear summary text
        additional_text = "" # Reset summary text variable

        ### Creating summary text for each article using spinbox results
        for article in wr_segments[:int(wr_spinbox.get())]:
            additional_text=additional_text+article[0]+"\nFrom Wired ["+article[4]+"]"+"\n\n"  

        for article in qt_segments[:int(qt_spinbox.get())]:
            additional_text=additional_text+article[0]+"\nFrom Queensland Times ["+article[4]+"]"+"\n\n"

        for article in cb_segments[:0]:
            additional_text=additional_text+article[0]+"\nFrom Canberra Times ["+article[4]+"]"+"\n\n"

        for article in gl_segments[:0]:
            additional_text=additional_text+article[0]+"\nFrom goulburn Post ["+article[4]+"]"+"\n\n"
   
        summary_text.insert(0.0,additional_text)
            
            
    # Setting geometry variables
    padding_size = 10
    spinbox_width = 2
    
    # Setting up window
    window = Tk()
    window.geometry("600x900") # Window size
    window.configure(background="white")
    window.title("IO.News") 

    ### Top frame - holds sources and logo
    top_frame = Frame(window,bg="white")
    top_frame.grid(column=1,row=1,sticky=W)
    
    ### Spinbox and sources - 0-10 - frame
    sources_frame = LabelFrame(top_frame,text="Sources", bg="white",font=("arial",18,"bold"),fg="dark red")
    sources_frame.grid(column=1,row=1,sticky=W,padx=padding_size,pady=padding_size)
    
    # Spinboxes
    wr_spinbox = Spinbox(sources_frame)
    wr_spinbox.grid(column=2,row=1,sticky=E)

    qt_spinbox = Spinbox(sources_frame)
    qt_spinbox.grid(column=2,row=2,sticky=E)

    cb_spinbox = Spinbox(sources_frame)
    cb_spinbox.grid(column=2,row=3,sticky=E)

    gl_spinbox = Spinbox(sources_frame)
    gl_spinbox.grid(column=2,row=4,sticky=E)

    # Settings for spinboxes
    for spinbox in (wr_spinbox,qt_spinbox,cb_spinbox,gl_spinbox):
        spinbox.configure(buttonbackground="white",font=("arial", 20),
        from_=0, to=10,width=spinbox_width,fg="dark red",command=spinbox_change)

    # News sources labels
    wr_text = "Wired  \n (13/9/2019)  "
    qt_text = "Queensland Times  \n (16/9/2019)  "
    cb_text = "Canberra Times  \n (today)  "
    gl_text = "Goulburn Post  \n (today)  "

    wr_label = Label(sources_frame,text=wr_text)
    wr_label.grid(column=1,row=1,sticky=E)

    qt_label = Label(sources_frame,text=qt_text)
    qt_label.grid(column=1,row=2,sticky=E)

    cb_label = Label(sources_frame,text=cb_text,fg="black")
    cb_label.grid(column=1,row=3,sticky=E)

    gl_label = Label(sources_frame,text=gl_text)
    gl_label.grid(column=1,row=4,sticky=E)

    for label in (wr_label,qt_label,cb_label,gl_label): # Settings for all source labels
        label.configure(justify=RIGHT,font=("arial", 16),bg="white")

    ### news logo image
    news_logo =  PhotoImage(file = "io_news_logo.png")
    logo_display = Label(top_frame,image = news_logo,bg="white",width=200,height=200)
    logo_display.grid(column=2,row=1,padx=padding_size,pady=padding_size,sticky=E)
    
    ### Export button
    export_btn = Button(window, text="Create Feed",relief=RIDGE,font=("arial",15),
    fg="white",bg="dark red",activebackground="white", command=export_stories)
    export_btn.grid(column=1,row=2,sticky=W,padx=padding_size,pady=padding_size)

    ### Save titles to database button
    db_headlines_spinbox = Spinbox(window, values=("Don't save to database","Save to database"),buttonbackground="white",font=("arial", 20),
        fg="dark red")
    db_headlines_spinbox.grid(column=1,row=3,sticky=W,padx=padding_size,pady=padding_size)

    ### Summary of articles selected using scroll text
    summary_text = ScrolledText(window,width=50, height=20,bg="white",font=("arial",14))
    summary_text.grid(column=1,columnspan=2,row=4,padx=padding_size,pady=padding_size)

    window.mainloop()

### Creating the html file
def html_create(wr,qt,cb,gl,
wired_number,qt_number,canberra_number,goulburn_number,database_option):

    # Split lists to required number of stories
    wr = wr[:int(wired_number)]
    qt = qt[:int(qt_number)]
    cb = cb[:0]
    gl = gl[:0]
    
    # Open html file for writing
    html_file = open(news_file_name,'w')

    # First section for html - heading and start of body tag
    html_string = """<!DOCTYPE html>
    <html>
    <heading>
    <style>
    body {
      font-family: Arial;
      display: block;
      margin-left: 30%;
      margin-right: 20%;
    }

    h1 {
      text-align: center;
      color: dark red;
      font-size: 250%;
    }

    img {
      display: block;
      margin-left: auto;
      margin-right: auto;
    }

    p1 {
      margin-left: auto;
      font-size: 175%;
      font-family: Arial;

    }

    p2 {
      text-align: center;
      margin-left: auto;
      font-size: 140%;
      padding-top: 100px;      
    }

    </style>
    </heading>
    <body>

        <img src="https://pagefair.com/wp-content/uploads/2013/09/blog6.jpg" width="400" height = "400">

    <br>

        <h1>IO.News</h1>

    <br>

        <h1>Your Personalised Feed</h1>
    
    <br><br><br>"""
    
    ### Repeated section using articles to input information
    for list_of_articles in (wr,qt,cb,gl): 
        for article in list_of_articles:
            html_string = html_string + """<img src="line_break_decor.png" width="100%" height="30%">

            <br><br><br>

                <h1>""" + article[0] + """</h1>

                <img src=""" + article[1] + """ width="500px" height="283">
            <br>

                <p1>""" + article[2] + """</p1>

            <br><br>

                <p2><a href=""" + article[3] + """>""" + article[3] + """</a>

            <br><br>
        
                [""" + article[4] + """]</p2>

            <br><br><br><br><br>"""

    ### Save to database section
    if database_option == "Save to database":
        
        for list_of_articles in (wr,qt,cb,gl): 
            for article in list_of_articles:
                if article[0] not in (news_log_db.fetchall())\
                and article[3] not in (news_log_db.fetchall())\
                and article[4] not in (news_log_db.fetchall()):    
                    text_1 = article[0]
                    text_2 = article[3]
                    text_3 = article[4]
                    sql = str('''INSERT INTO selected_stories
                            (headline,news_feed,publication_date)
                            VALUES ("''' + str(text_1) + '''","''' + str(text_2) + '''","''' +
                            str(text_3) + '''"); ''')

                news_log_db.execute(sql)

        # Save changes to database, then close the database
        connection.commit()
        news_log_db.close()
        connection.close()

        
    ### Footer section and closing of html tag
    # Links to all source news feeds
    html_string = html_string + """<img src="line_break_decor.png" width="70%" height="30%">
    <br><br>
    <p2>-Wired: <a href = "https://www.wired.com/feed">https://www.wired.com/feed</a></p2>
    <br>
    <p2>-Queensland Times: <a href = "https://www.qt.com.au/feeds/rss/homepage/">https://www.qt.com.au/feeds/rss/homepage/</a></p2>
    <br>
    <p2>-Canberra Times: <a href = "https://www.canberratimes.com.au/rss.xml">https://www.canberratimes.com.au/rss.xml/p1</a> </p2>
    <br>
    <p2>-Goulburn Post <a href = "https://www.goulburnpost.com.au/rss.xml">https://www.goulburnpost.com.au/rss.xml</a> </p2>
    <br><br>
    </body>
    </html>"""
    
    # Saving html file so it updates with new information
    html_file.write(html_string)
    html_file.close()

# Run function to get news text so it is up to date
update_news_info()




