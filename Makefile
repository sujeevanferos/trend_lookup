# ============================================================
#  Makefile for ML Model Training (CPU/GPU + Logs + Progress)
# ============================================================

# Python interpreter
PYTHON := python3

# Training scripts
CAT_SCRIPT := preprocessing/1_categorization_train.py
OPP_SCRIPT := preprocessing/2_opportunity_train.py

# Output model dirs
CAT_MODEL_DIR := preprocessing/categorization_model
OPP_MODEL_DIR := preprocessing/opportunity_model

# Virtual environment (optional)
VENV := venv

# Colors
Y := \033[33m
G := \033[32m
R := \033[31m
B := \033[34m
NC := \033[0m

# ============================================================
#  Device Switch Logic
# ============================================================
# Default = auto (use GPU if available)
# Override:
#   make train GPU=1
#   make train CPU=1

ifeq ($(GPU),1)
	DEVICE := cuda
else ifeq ($(CPU),1)
	DEVICE := cpu
else
	DEVICE := auto
endif

export DEVICE

# ============================================================
#  Logging
# ============================================================
# Enable logging:
#   make train LOG=1

ifeq ($(LOG),1)
	CAT_LOG := --log
	OPP_LOG := --log
else
	CAT_LOG :=
	OPP_LOG :=
endif

# ============================================================
#  Help Menu
# ============================================================
help:
	@echo "$(B)-----------------------------------------$(NC)"
	@echo " ML Training Makefile - Commands:"
	@echo "$(B)-----------------------------------------$(NC)"
	@echo "$(G) make venv$(NC)           - Create virtual environment"
	@echo "$(G) make install$(NC)        - Install requirements"
	@echo "$(G) make train-cat$(NC)      - Train categorization model"
	@echo "$(G) make train-opp$(NC)      - Train opportunity model"
	@echo "$(G) make train$(NC)          - Train BOTH models"
	@echo "$(G) make clean-models$(NC)   - Delete old models"
	@echo "$(G) make clean$(NC)          - Full cleanup"
	@echo "$(Y) Flags: GPU=1, CPU=1, LOG=1$(NC)"
	@echo "$(Y) Example: make train GPU=1 LOG=1$(NC)"
	@echo "$(B)-----------------------------------------$(NC)"

# ============================================================
#  Virtual Environment
# ============================================================
venv:
	$(PYTHON) -m venv $(VENV)
	@echo "$(G)Virtual environment created.$(NC)"
	@echo "Run: source venv/bin/activate"

install:
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	@echo "$(G)Dependencies installed.$(NC)"

# ============================================================
#  Training Commands
# ============================================================
train-cat:
	@echo "$(B)-----------------------------------------$(NC)"
	@echo "$(Y) Training Categorization Model (DEVICE=$(DEVICE))$(NC)"
	@echo "$(B)-----------------------------------------$(NC)"
	DEVICE=$(DEVICE) $(PYTHON) $(CAT_SCRIPT) $(CAT_LOG)
	@echo "$(G)Categorization model training completed.$(NC)"

train-opp:
	@echo "$(B)-----------------------------------------$(NC)"
	@echo "$(Y) Training Opportunity Model (DEVICE=$(DEVICE))$(NC)"
	@echo "$(B)-----------------------------------------$(NC)"
	DEVICE=$(DEVICE) $(PYTHON) $(OPP_SCRIPT) $(OPP_LOG)
	@echo "$(G)Opportunity model training completed.$(NC)"

train: train-cat train-opp
	@echo "$(G)-----------------------------------------$(NC)"
	@echo " All models trained successfully."
	@echo "-----------------------------------------$(NC)"

# ============================================================
#  Clean Up
# ============================================================
clean-models:
	rm -rf $(CAT_MODEL_DIR)
	rm -rf $(OPP_MODEL_DIR)
	@echo "$(R)Removed old model directories.$(NC)"

clean: clean-models
	rm -rf __pycache__
	rm -rf *.pyc
	@echo "$(R)Cleanup complete.$(NC)"

