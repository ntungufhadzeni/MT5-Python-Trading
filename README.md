# MT5-Python-Trading

**MT5-Python-Trading** is a project that enables algorithmic trading with MetaTrader 5 using Python. This repository provides tools and scripts to automate trading strategies, manage positions, and analyze historical data.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Usage](#usage)

## Introduction

This project aims to simplify algorithmic trading on MetaTrader 5 by leveraging the power of Python. It includes modules for opening/closing positions, retrieving historical data, and implementing various trading strategies.

## Features

- **Automated Trading:** Execute trading strategies automatically.
- **Position Management:** Open, close, and manage trading positions.
- **Historical Data Analysis:** Retrieve and analyze historical trading data.
- **Break-Even Adjustment:** Automatically adjust stop-loss to break-even.

## Requirements

- MetaTrader 5 terminal installed on your machine.
- Python 3.x installed.
- Required Python packages (specified in `requirements.txt`).

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ntungufhadzeni/MT5-Python-Trading.git
   cd MT5-Python-Trading
   
2. **Create virtual environment and Install the required Python packages:**
    
   ```bash
   python -m venv .venv
   .venv/Scripts/Activate.ps1
   pip install -r requirements.txt

## Getting Started
1. Open your MetaTrader 5 terminal and ensure it is connected to your trading account.

2. Configure the .env file with your MetaTrader 5 login details.
   ```bash
   SERVER=<your MT5 server>
   LOGIN=<your MT5 account number>
   PASSWORD=<your password>

3. Explore the provided examples and adapt them to your trading strategy.


## Usage
1. Run the Python scripts to execute your trading strategies.
   ```bash
   python main.py
2. Customize the provided scripts or create your own based on the requirements.
3. Refer to the documentation for detailed information on each module.
   
