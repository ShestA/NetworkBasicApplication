ifeq ($(COMMON_LIB_PATH ),)
  COMMON_LIB_PATH  = $(CURDIR)/common_lib
endif
common_lib:
	cd $(COMMON_LIB_PATH) && $(MAKE)
.PHONY: common_lib

ifeq ($(NETWORK_LIB_PATH ),)
  NETWORK_LIB_PATH  = $(CURDIR)/network_lib
endif
network_lib:
	cd $(NETWORK_LIB_PATH) && $(MAKE)
.PHONY: network_lib

libs: common_lib network_lib
.PHONY: libs

all: libs
.PHONY: all

default_target:
	all
.PHONY: default_target
