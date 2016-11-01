
class Initializer(object):
    def __init__(self):

        magentaprint("LosHelper initializing...", False)

        self.bot_thread = None
        self.mud_map = None
        self.threaded_map_setup = True

        if self.threaded_map_setup:
            # Threading the db setup causes a locking error if the starting area needs to be saved
            self.bot_ready = False
            self.mud_map_thread = threading.Thread(target=self.setup_mud_map)
            # self.mud_map_thread.start()  # Don't forget to uncomment .join()
        else:
            # # self.mud_map = MudMap()
            # # self.bot_ready = self.mud_map.ready  # True
            # self.mud_map_thread = threading.Thread(target=magentaprint, args=("setting up mud map in main thread",))
            self.setup_mud_map()

        self.character = Character()

        sys.argv = [s.strip() for s in sys.argv]  # removes \r since git can add them to run.sh

        if "-fake" in sys.argv:
            self.telnetHandler = FakeTelnetHandler()
            # sys.argv.remove("-fake")
        else:
            self.telnetHandler = TelnetHandler()

        if self.threaded_map_setup:
            self.mud_map_thread.start()  # Don't forget to uncomment .join()
        self.consoleHandler = newConsoleHandler() 
        self.MUDBuffer = MyBuffer()
        self.mudListenerThread = MudListenerThread(self.telnetHandler, self.MUDBuffer)
        self.mudReaderThread = MudReaderThread(self.MUDBuffer, self.character, self.consoleHandler)
        self.mudReaderHandler = MudReaderHandler(self.mudReaderThread, self.character)
        self.inventory = Inventory(self.mudReaderHandler, self.telnetHandler, self.character)
        self.character.inventory = self.inventory
        self.mudReaderHandler.add_subscriber(self.character.mobs)
        self.combat_reactions = CombatReactions(self.mudReaderHandler, self.character)

        # self.mud_map_thread.start()  # Don't forget to uncomment .join()
        self.mudListenerThread.start()
        self.mudReaderThread.start()

        # With the MUDReaderThread going, we have the server's text and prompts now showing
        # if self.threaded_map_setup:
        #     magentaprint("LosHelper joining mud_map_thread.")  # Ha this print can cause the lock error
        #     self.mud_map_thread.join() 
        self.write_username_and_pass()
        self.initialize_reactions()
        self.check_class_and_level()
        self.check_spells()
        self.check_info()

        self.commandHandler = CommandHandler(self.character, self.mudReaderHandler, self.telnetHandler)
        self.cartography = Cartography(self.mudReaderHandler, self.commandHandler, self.character)
        self.commandHandler.go.cartography = self.cartography  
            # Cartography shouldn't need commandHandler to fix dependencies
        self.character.TRYING_TO_MOVE = True  # required for mapping (Hack - look into this - better init for Goto)
        self.telnetHandler.write('l')  # Sets area id for mapping
        self.commandHandler.go.wait_for_flag()
        self.check_inventory()

    def setup_mud_map(self):
        magentaprint("Generating the mapfile....", False)
        self.mud_map = MudMap()
        magentaprint("LosHelper: Mapfile generated", False)
        self.bot_ready = True
    
    def close(self):
        self.mudListenerThread.stop()
        self.mudReaderThread.stop()
        if self.threaded_map_setup:
            self.mud_map_thread.join()
        self.mudListenerThread.join(10)
        self.mudReaderThread.join(10)
        self.telnetHandler.close()
        flush_input()

        try:
            # Maybe it's better to remove on startup.
            os.remove("no.db")
        except OSError as e:
            if hasattr(e, 'errno') and e.errno != 2:
                # errno 2 means the file's not there.
                magentaprint("LosHelper os.remove(\"no.db\") error: " + str(e))

        magentaprint("Closed telnet.")
        magentaprint("Threads remaining: " + str(threading.active_count()))

    def write_username_and_pass(self):
        args = [s for s in sys.argv[1:] if not s.startswith('-')]
        magentaprint("LosHelper stripped args: " + str(args))

        if len(args) >= 1:
            self.character.name = args[0].title()
        else:
            self.character.name = input()

        self.telnetHandler.write(self.character.name)

        if len(args) >= 2:
            password = args[1]
        else:
            password = getpass.getpass("")

        self.telnetHandler.write(password)

        # if len(args) >= 2:
        #     self.character.name = args[1].title()
        #     self.telnetHandler.write(self.character.name)
        #     password = args[2]
        # else:
        #     # With the MUD thread going already, there is no need to prompt here.
        #     self.character.name = input()
        #     self.telnetHandler.write(self.character.name)
        #     password = getpass.getpass("")

        # self.telnetHandler.write(password)

    def initialize_reactions(self):
        self.mudReaderHandler.register_reaction(WieldReaction(self.character, self.telnetHandler))

    def check_inventory(self):
        # This prints the inventory.  I like that.  
        # Inventory needs this to be up to date.
        self.character.inventory.get_inventory()
        self.character.inventory.output_inventory()

    def check_class_and_level(self):
        whois = Whois(self.mudReaderHandler, self.telnetHandler, self.character)
        whois.execute(self.character.name)
        whois.wait_for_flag()
        self.character._class = CharacterClass(self.telnetHandler, self.character.class_string, self.character.level)
        # self.character.CAST_PERIOD = self.character._class.cast_wait
        # self.character.CAST_WAIT = self.character._class.cast_wait
        self.character.configure_health_and_mana_variables()
        self.character.set_monster_kill_list()
        magentaprint("LosHelper ability list: " + str(self.character._class.abilities))
        for a in self.character._class.abilities.values():
            # self.mudReaderHandler.register_reaction(a)
            magentaprint("Added subscriber " + str(a))
            self.mudReaderHandler.add_subscriber(a)

    def check_spells(self):
        # magentaprint("LosHelper.check_spells() sleeping 2 sec.")
        # time.sleep(2)
        spells = Spells(self.telnetHandler, self.character)
        self.mudReaderHandler.add_subscriber(spells)
        spells.execute()
        spells.wait_for_flag()

    def check_info(self):
        info = Info(self.mudReaderHandler, self.telnetHandler, self.character)
        info.execute()
        magentaprint("LosHelper.check_info() calling character.process_info()")
        self.character.process_info()
