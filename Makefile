ifeq ($(LIBS_DIR),)
  LIBS_DIR = $(CURDIR)/libs
endif

ifeq ($(SERVER_SRC),)
  SERVER_SRC = $(CURDIR)/server
endif

ifeq ($(CLIENT_SRC),)
  CLIENT_SRC = $(CURDIR)/client
endif

libs:
	cd $(LIBS_DIR) && $(MAKE)
.PHONY: libs

client: libs
	cd $(CLIENT_SRC) && $(MAKE)
.PHONY: client

server: libs
	cd $(SERVER_SRC) && $(MAKE)
.PHONY: server

all: libs client server
.PHONY: all
