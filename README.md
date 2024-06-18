# Streaming-Function Console Application

## Overview

This project is a console-based application that interacts with OpenAI's Assistant API to provide real-time responses using streaming functionality. The application features  streaming of assistant responses and the cabilty of Function Calling


- **Streaming**: This code utlizies openai's streaming function cabilties along with its Assistant api.
- **Function Calling**: In adition to the Streaming you can also implement your own functions in this code.

## Requirements

- Python 3.12
- `rich` library for enhanced console output
- `msvcrt` (available on Windows) for capturing keyboard input
- `Openai` OpenAI
- An OpenAI API key / Acount


## Installation

1. Clone the repositoryt.
2. Install the required Python packages:
    ```sh
    pip install rich Openai
    ```

## Usage

1. Replace `PLACE YOUR API KEY HERE ` in the script with your actual OpenAI API key.
2. Run the script:
    ```sh
    python main.py
    ```
