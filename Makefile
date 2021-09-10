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

install_libs:
	python3 -m pip install libs/common_lib
	python3 -m pip install libs/network_lib
.PHONY: install

tests:
	pytest -rx --capture=no --full-trace .ci
.PHONY: tests

clean:
	find  . -name '__pycache__' -prune -exec rm -rf {} \;
	find . -d -name 'dist' -prune -exec rm -rf {} \;
	find . -d -name 'build' -prune -exec rm -rf {} \;
	find . -d -name '*.egg-info' -prune -exec rm -rf {} \;
	find . -d -name '*.spec' -prune -exec rm -rf {} \;
	find . -d -name '*.log' -prune -exec rm -rf {} \;
.PHONY: clean
