from socket import *
from datetime import *
import pickle
import threading

activeUser = []
activeGroup = []
currentUser = ""
authenticated = False

def sort(postlist):
    host = []
    for i in range(0, len(postlist)):
        if postlist[i].read == True:
            post = postlist[i]
            host.append(post)
    for post in host:
        postlist.remove(post)
        postlist.append(post)

class Post:
    def __init__(self, postID, subject, author, date, data):
        self.postID = postID
        self.subject = subject
        self.author = author
        self.date = date
        self.data = data
        self.read = False


class Group:
    def __init__(self, groupID, name):
        self.groupID = groupID
        self.name = name
        self.postArray = []
        self.subscribedUsers = []


#initialize some groups and posts
# group1 = Group(0,"comp.programming")
# group2 = Group(1,"comp.os.threads")
# group3 = Group(2,"comp.lang.c")
# group4 = Group(3,"comp.lang.python")
# group5 = Group(4,"comp.lang.javascript")
# group6 = Group(5,"comp.stonybrook")
# group7 = Group(6,"comp.nyu")
# group8 = Group(7,"comp.c++")
# group9 = Group(8,"comp.ruby")
# group10 = Group(9,"comp.java")
# group11 = Group(10,"comp.object")
# group12 = Group(11,"comp.algorithm")
# group13 = Group(12,"comp.recursion")
# group14 = Group(13,"comp.os")
# group15 = Group(14,"comp.lang.assembly")


# self.subscribedUsers = []


# initialize some groups and posts

# activeGroup.append(group1)
# activeGroup.append(group2)
# activeGroup.append(group3)
# activeGroup.append(group4)
# activeGroup.append(group5)
# activeGroup.append(group6)
# activeGroup.append(group7)
# activeGroup.append(group8)
# activeGroup.append(group9)
# activeGroup.append(group10)
# activeGroup.append(group11)
# activeGroup.append(group12)
# activeGroup.append(group13)
# activeGroup.append(group14)
# activeGroup.append(group15)


with open('serverData.pkl', 'rb') as f:
    activeGroup = pickle.load(f)

serverPort = 12001
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(5)
print ('The server is ready to receive, the port number is ' + str(serverPort))


class loginThread(threading.Thread):
    def __init__(self,connectionSocket ):
        super(loginThread, self).__init__()
        self.connectionSocket = connectionSocket
        self.running = True
        self._stop = threading.Event()

    def run(self):
        isConnectToClient = True

        while isConnectToClient==True:
            commandsOriginal = self.connectionSocket.recv(1024)
            commandsAll = commandsOriginal.split()
            firstcommand = commandsAll[0]
            print (commandsOriginal)

            if commandsOriginal == "exit":
                self.connectionSocket.send("client exit")
                self.connectionSocket.close()
                self.stop()
                break

            elif commandsOriginal == "help":
                self.connectionSocket.send("print usage")

            elif firstcommand == "login":
                userID = commandsAll[1]

                if userID not in activeUser:
                    activeUser.append(userID)
                    currentUser = userID
                    authenticated = True

                #history parser
                    if len(commandsAll)>2:
                        i = 2
                        while i < len(commandsAll):
                            # history is in the form of 1-2,3-4, 1-x
                            history = str(commandsAll[i]).split("-")

                            group = int(history[0])
                            if userID not in activeGroup[group].subscribedUsers:
                                activeGroup[group].subscribedUsers.append(userID)

                            if str(history[1]) != 'x':
                                post = int(history[1])
                                if post < len(activeGroup[group].postArray):
                                    activeGroup[group].postArray[post].read = True
                            i += 1

                    #Send protocol back to client
                    self.connectionSocket.send("login success")
                    while self.running == True:
                        firstcommand =""
                        buffer = ""
                        commandsAll = self.connectionSocket.recv(1024).split()

                        firstcommand = commandsAll[0]

                        if firstcommand =="saveServer":
                            with open('serverData.pkl', 'wb') as output:
                                pickle.dump(activeGroup, output, pickle.HIGHEST_PROTOCOL)
                            self.connectionSocket.send("Server Data has been updated")

                        elif firstcommand == "ag":
                            index = 0  # index in the activeGroup Array
                            quit = False
                            optionalcommand = 5

                            if len(commandsAll) > 1:
                                optionalcommand = int(commandsAll[1])
                                #here uses the default value for N -> showing N items at a time

                            while index < optionalcommand:
                                if currentUser not in getattr(activeGroup[index], 'subscribedUsers'):
                                    buffer += str(index) + '. ( )     ' + getattr(activeGroup[index], 'name') + '\n'
                                else:
                                    buffer += str(index) + '. (s)     ' + getattr(activeGroup[index], 'name') + '\n'
                                index += 1

                            self.connectionSocket.send(buffer)

                            while quit==False:

                                buffer = "'"

                                subcommand = self.connectionSocket.recv(1024).split()

                                if subcommand[0] == 's':
                                    temp = 1
                                    while temp<len(subcommand):
                                        #subscribe to index + argument group
                                        if int(subcommand[temp])< index:
                                            groupToSubscribe = getattr(activeGroup[int(subcommand[temp])], 'subscribedUsers')
                                            buffer += "Subscribing group " + getattr(activeGroup[int(subcommand[temp])],'name')+'\n'
                                            # activeGroup[groupToSubscribe].getUserArray.AddtoGroup
                                            if currentUser not in groupToSubscribe:
                                                groupToSubscribe.append(currentUser)

                                        else:
                                            print ("index out of bound")

                                        temp += 1
                                    self.connectionSocket.send(buffer)

                                elif subcommand[0] == 'u':
                                    temp = 1
                                    while temp<len(subcommand):
                                        ##subscribe to index + argument group
                                        if int(subcommand[temp])< index:
                                            groupToUnsubscribe = getattr(activeGroup[int(subcommand[temp ])], 'subscribedUsers')
                                            buffer += "UNSubscribing group " + getattr(activeGroup[int(subcommand[temp])],'name')+'\n'
                                            # activeGroup[groupToSubscribe].getUserArray.Remove
                                            if currentUser in groupToUnsubscribe:
                                                groupToUnsubscribe.remove(currentUser)
                                        else:
                                            print ("index out of bound")
                                        temp += 1
                                    self.connectionSocket.send(buffer)

                                elif subcommand[0] == 'n':
                                    # list next set of group
                                    temp = 0

                                    while temp < optionalcommand:
                                        if index > len(activeGroup)-1:
                                            buffer += "------All Group Has Been Shown------"+'\n'
                                            quit = True
                                            break
                                        elif currentUser not in getattr(activeGroup[index], 'subscribedUsers'):
                                            buffer += str(index) + '. ( )     ' + getattr(activeGroup[index], 'name') + '\n'
                                        elif currentUser  in getattr(activeGroup[index], 'subscribedUsers'):
                                            buffer += str(index) + '. (s)     ' + getattr(activeGroup[index], 'name') + '\n'
                                        index += 1
                                        temp += 1
                                    self.connectionSocket.send(buffer)

                                elif subcommand[0] == 'q':

                                    temp = 0

                                    while temp < len(activeGroup):
                                        ##### print all group before finishing
                                        if currentUser not in getattr(activeGroup[temp], 'subscribedUsers'):
                                            buffer += str(temp) + '. ( )     ' + getattr(activeGroup[temp], 'name') + '\n'
                                        else:
                                            buffer += str(temp) + '. (s)     ' + getattr(activeGroup[temp], 'name') + '\n'
                                        temp += 1
                                    self.connectionSocket.send(buffer)
                                    quit = True
                                    break
                                else :
                                    self.connectionSocket.send('input invalid')

                        elif firstcommand == "sg":
                            index = 0  # index in the activeGroup Array
                            count = 0
                            buffer = ""
                            quitSG = False
                            optionalcommand = 5
                            if len(commandsAll) > 1:
                                optionalcommand = int(commandsAll[1])

                            # here uses the default value for N -> showing N items at a time
                            while count < optionalcommand and index < len(activeGroup):
                                # list all the group up to N
                                if currentUser in getattr(activeGroup[index], 'subscribedUsers'):

                                    unreadPost = 0
                                    groupPost = getattr(activeGroup[index], 'postArray')
                                    for x in range(0, len(groupPost)):
                                        if groupPost[x].read == False:
                                            unreadPost += 1

                                    buffer += str(index) + '. '+str(unreadPost) +' '+ getattr(activeGroup[index], 'name') + '\n'
                                    count += 1
                                index += 1
                            self.connectionSocket.send(buffer)

                            while quitSG == False:

                                buffer = "'"
                                subcommand = self.connectionSocket.recv(1024).split()
                                if subcommand[0] == 'u':
                                    temp = 1
                                    while temp < len(subcommand):
                                        if int(subcommand[temp])< index:
                                            ##subscribe to index + argument group
                                            groupToUnsubscribe = getattr(activeGroup[int(subcommand[temp])], 'subscribedUsers')
                                            buffer += "Unsubscribing group " + getattr(activeGroup[int(subcommand[temp])],'name')+'\n'

                                            if currentUser in groupToUnsubscribe:
                                                groupToUnsubscribe.remove(currentUser)

                                        else:
                                            print ("index out of bound")
                                        temp += 1
                                    self.connectionSocket.send(buffer)
                                elif subcommand[0] == 'n':
                                    temp = 0
                                    count = 0
                                    while count < optionalcommand and index < len(activeGroup):
                                        if index > len(activeGroup):
                                            buffer += "------All Group Has Been Shown------"
                                            quit = True
                                            break

                                        if currentUser in getattr(activeGroup[index], 'subscribedUsers'):
                                            unreadPost = 0
                                            groupPost = getattr(activeGroup[index], 'postArray')
                                            for x in range(0, len(groupPost)):
                                                if groupPost[x].read == False:
                                                    unreadPost += 1

                                            buffer += str(index) + '. '+str(unreadPost) +' '+ getattr(activeGroup[index], 'name') + '\n'
                                            count+=1
                                        index += 1
                                        temp += 1
                                    self.connectionSocket.send(buffer)

                                elif subcommand[0] == 'q':
                                    temp = 0

                                    while temp < len(activeGroup):
                                        ##### print all group before finishing
                                        if currentUser in getattr(activeGroup[temp], 'subscribedUsers'):
                                            unreadPost = 0
                                            groupPost = getattr(activeGroup[temp], 'postArray')
                                            for x in range(0, len(groupPost)):
                                                if groupPost[x].read == False:
                                                    unreadPost += 1

                                            buffer += str(temp) + ' '+str(unreadPost) +' '+ getattr(activeGroup[temp], 'name') + '\n'

                                        temp += 1
                                    self.connectionSocket.send(buffer)
                                    quitSG = True
                                    break

                                else:
                                    self.connectionSocket.send('sg input invalid\n')

                        elif firstcommand == "rg":
                            buffer = ""
                            currentGroup = Group(-1, "temp")
                            foundGroup = False
                            if len(commandsAll) >= 2:
                                for group in activeGroup:
                                    if commandsAll[1] == group.name:
                                        currentGroup = group
                                        foundGroup = True
                                        break
                                if foundGroup == True:
                                    defaultN = 5
                                    if len(commandsAll) > 2:
                                        defaultN = int(commandsAll[2])

                                    if defaultN > len(currentGroup.postArray):
                                        defaultN = len(currentGroup.postArray)

                                    if currentUser in currentGroup.subscribedUsers:
                                        sort(currentGroup.postArray)
                                        temp = defaultN
                                        for i in range(0, defaultN):
                                            post = currentGroup.postArray[i]
                                            if(post.read == True):
                                                buffer += str(i) + '.  ' + post.date + '  ' + post.subject + '\n'
                                            else:
                                                buffer += str(i) + '. N ' + post.date + '  ' + post.subject + '\n'
                                        self.connectionSocket.send(buffer)
                                        while 1:
                                            cmd = self.connectionSocket.recv(1024).split()

                                            subcommand = cmd[0].replace('\r\n', '')
                                            buffer = ''
                                            if subcommand.isdigit():

                                                if int(subcommand) in range(0, defaultN):
                                                    currentpost = currentGroup.postArray[int(subcommand)]
                                                    currentpost.read = True
                                                    start = 0
                                                    end = defaultN
                                                    postdiv = currentpost.data.split('\n')
                                                    buffer += 'Group : ' + currentGroup.name + '\n'
                                                    buffer += 'Subject : ' + currentpost.subject + '\n'
                                                    buffer += 'Author : ' + currentpost.author + '\n'
                                                    buffer += 'Date : ' + currentpost.date + '\n\n'
                                                    if (end > len(postdiv)):
                                                        end = len(postdiv)
                                                    for linenum in range(start, end):
                                                        buffer += postdiv[linenum] + '\n'
                                                    self.connectionSocket.send(buffer)

                                                    while 1:
                                                        buffer = ''
                                                        subsubcommand = self.connectionSocket.recv(1024).split()
                                                        if subsubcommand[0] == 'n':

                                                            if end >= len(postdiv):
                                                                buffer = ''
                                                                self.connectionSocket.send(
                                                                    'the post is all read, go back to rg menu \n')
                                                                sort(currentGroup.postArray)
                                                                for j in range(0, defaultN):
                                                                    post = currentGroup.postArray[j]
                                                                    if (post.read == True):
                                                                        buffer += str(
                                                                            j) + '.  ' + post.date + '  ' + post.subject + '\n'
                                                                    else:
                                                                        buffer += str(
                                                                            j) + '. N ' + post.date + '  ' + post.subject + '\n'
                                                                self.connectionSocket.send(buffer)
                                                                break
                                                            else:
                                                                start = end
                                                                end = start+defaultN
                                                                if end > len(postdiv):
                                                                    end = len(postdiv)

                                                            for linenum in range(start, end):
                                                                buffer += postdiv[linenum] + '\n'
                                                            self.connectionSocket.send(buffer)

                                                        elif subsubcommand[0] == 'q':
                                                            sort(currentGroup.postArray)
                                                            for j in range(0, defaultN):
                                                                post = currentGroup.postArray[j]
                                                                if (post.read == True):
                                                                    buffer += str(j) + '.  ' + post.date + '  ' + post.subject + '\n'
                                                                else:
                                                                    buffer += str(j) + '. N ' + post.date + '  ' + post.subject + '\n'
                                                            self.connectionSocket.send(buffer)
                                                            break
                                                        else:
                                                            connectionSocket.send('invalid cmd')

                                                else :
                                                    connectionSocket.send("Please give a valid line number start from 0( not post number) \n")
                                            elif cmd[0] == 'r':
                                                if len(cmd) < 2:
                                                    self.connectionSocket.send('invalid r cmd')
                                                else:
                                                    postnum = cmd[1].split('-')
                                                    if len(postnum) == 1:
                                                        # only mark one post
                                                        buffer += 'mark post ' + postnum[0] + 'as reader' + '\n'
                                                        currentGroup.postArray[int(postnum[0])].read = True
                                                        self.connectionSocket.send(buffer)

                                                    else:
                                                        for k in range(int(postnum[0]), int(postnum[1]) + 1):
                                                            # mark all the post
                                                            buffer += 'mark post ' + str(k) + 'as readed' + '\n'
                                                            currentGroup.postArray[k].read = True
                                                        self.connectionSocket.send(buffer)

                                            elif cmd[0] == 'n':
                                                buffer = ''

                                                if temp < len(currentGroup.postArray):
                                                    start = temp
                                                    end = start+ defaultN
                                                    if end > len(currentGroup.postArray):
                                                        end = len(currentGroup.postArray)
                                                    temp = end
                                                    sort(currentGroup.postArray)
                                                    for it in range(start, end):
                                                        post = currentGroup.postArray[it]
                                                        if (post.read == True):
                                                            buffer += str(it) + '.  ' + post.date + '  ' + post.subject + '\n'
                                                        else:
                                                            buffer += str(it) + '. N ' + post.date + '  ' + post.subject + '\n'
                                                    self.connectionSocket.send(buffer)

                                                else:
                                                    self.connectionSocket.send('all post is shown, exist the rg menu \n')
                                                    break



                                            elif cmd[0] == 'p':
                                                postid = str(currentGroup.groupID) + '-' + str(len(currentGroup.postArray) + 1)
                                                self.connectionSocket.send('Please Give a Subject of your new post\n')
                                                subject = self.connectionSocket.recv(1024).replace('\r\n', '')
                                                self.connectionSocket.send('Please Give the Content of your new post, end by %(end)\n')
                                                content = self.connectionSocket.recv(1024).replace('\r\n', '') + '\n'
                                                contentcont = content
                                                while contentcont.find('%(end)') == -1:
                                                    self.connectionSocket.send('>>>')
                                                    contentcont = ''
                                                    contentcont += self.connectionSocket.recv(1024).replace('\r\n', '')
                                                    content += contentcont + '\n'
                                                content = content.replace('%(end)', '')

                                                date = datetime.now().strftime("%I:%M %p, %B %d,%Y")

                                                NPost = Post(postid, subject, currentUser, date, content)
                                                currentGroup.postArray.insert(0, NPost)
                                                buffer += 'Post Created \n'
                                                for i in range(0, defaultN):
                                                    post = currentGroup.postArray[i]
                                                    if (post.read == True):
                                                        buffer += str(i) + '.  ' + post.date + '  ' + post.subject + '\n'
                                                    else:
                                                        buffer += str(i) + '. N ' + post.date + '  ' + post.subject + '\n'
                                                self.connectionSocket.send(buffer)

                                            elif cmd[0] == 'q':
                                                self.connectionSocket.send('quit rg menu, back to main menu\n')
                                                break
                                            else:
                                                self.connectionSocket.send('input invalid\n')

                                    else:
                                        self.connectionSocket.send('You are not subscribe this group \n')

                                else:
                                    self.connectionSocket.send("The Group is invalid\n")

                            else:
                                self.connectionSocket.send('invalid rg cmd ex: rg [groupname] (optional: number) \n')

                        elif firstcommand == "logout":
                            # remove user from activeUser array
                            activeUser.remove(currentUser)
                            self.connectionSocket.send("logout success")
                            #################send history to client##################
                            historyCount = 0
                            historyString = ""
                            for tempGroup in activeGroup:
                                subUsers = getattr(tempGroup, 'subscribedUsers')
                                if currentUser in subUsers:
                                    if historyCount!=0:
                                        historyString = historyString+' '
                                    historyCount = 1
                                    historyString = historyString+str(tempGroup.groupID)+'-x'
                                    for tempPost in tempGroup.postArray:
                                        if(tempPost.read == True):
		                                    historyString = historyString+' '
		                                    historyString = historyString+str(tempGroup.groupID)+'-'+str(tempPost.postID-1)
		                                    tempPost.read = False
                                    subUsers.remove(currentUser)

                            temp_message = self.connectionSocket.recv(1024)
                            self.connectionSocket.send(historyString)
                            self.connectionSocket.close()
                            self.stop()
                            #################send history to client##################
                            isConnectToClient = False
                            break
                        else:
                            self.connectionSocket.send("invalid command")
                else:
                    # send protocol to tell client enter another id
                    self.connectionSocket.send("login failed")
            else:
                self.connectionSocket.send("invalid command")

    def stop(self):
        self._stop.set()


while 1:
    (connectionSocket, addr) = serverSocket.accept()
    loginThread(connectionSocket).start()
