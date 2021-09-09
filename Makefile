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

clean:
	find . -name __pycache__ -exec rm -rf {} \;
	find . -name '*.spec' -exec rm -rf {} \;
	find . -name dist -exec rm -rf {} \;
	find . -name build -exec rm -rf {} \;
	find . -name '*.egg-info' -exec rm -rf {} \;
	find . -name '*.log' -exec rm -rf {} \;

.PHONY: clean
