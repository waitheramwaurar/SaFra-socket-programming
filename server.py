#!/usr/bin/env python3

# import os
import time
import logging
import threading
import socket as s
import configparser

# Constants
PORT = 5067
BUFFER_SIZE = 1024
REREAD_ON_QUERY = True
AVERAGE_EXECUTION_TIME_TRUE = 0.04  # 40 milliseconds in seconds
AVERAGE_EXECUTION_TIME_FALSE = 0.0005  # 0.5 milliseconds in seconds

# Load configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Set up logging
logging.basicConfig(filename='server_log.txt', level=logging.DEBUG)


# Function to read the file content only if REREAD_ON_QUERY is True
def read_file_content(file_path):
    if REREAD_ON_QUERY:
        with open(file_path, 'r') as file:
            return file.read()
    else:
        return None


# Function to handle client connection
def handle_client(cs, address):
    try:
        # Receive data from the client
        data = cs.recv(BUFFER_SIZE).decode('utf-8').rstrip('\x00')

        # Measure execution time
        start_time = time.time()

        # Read the file content
        file_path = config['DEFAULT']['linuxpath']
        file_content = read_file_content(file_path)

        # Check if the string exists in the file
        if data in file_content:
            response = "STRING EXISTS\n"
        else:
            response = "STRING NOT FOUND\n"

        # Calculate execution time
        execution_time = time.time() - start_time

        # Log the debug information
        logging.debug(
            f"Query - {data}, IP - {address}, Execution Time - {execution_time}s\n")
        print(
            f"Query - {data}, IP - {address}, Execution Time - {execution_time}s\n")

        # Send the response to the client
        cs.send(response.encode('utf-8'))
    except Exception as e:
        # Handle exceptions and log errors
        logging.error(f"{str(e)}")
        print(f"[ERROR] {str(e)}")

    finally:
        # Close the client socket
        cs.close()


# Function to run the server
def main():
    # Create a server socket object
    ss = s.socket(s.AF_INET, s.SOCK_STREAM)

    # Bind the socket to a specific address and port
    ss.bind(('0.0.0.0', PORT))

    # Listen for incoming connections
    ss.listen(5)

    logging.info(f'Server listening on port {PORT}')
    print(f'[INFO] Server listening on port {PORT}')

    try:
        while True:
            # Measure execution time without processing a query
            start_time = time.time()
            file_path = config['DEFAULT']['linuxpath']
            read_file_content(file_path)
            execution_time = time.time() - start_time

            # Adjust the sleep time based on the REREAD_ON_QUERY flag
            if REREAD_ON_QUERY:
                sleep_time = max(
                    0, AVERAGE_EXECUTION_TIME_TRUE - execution_time)
            else:
                sleep_time = max(
                    0, AVERAGE_EXECUTION_TIME_FALSE - execution_time)

            # Sleep to meet the average execution time requirement
            time.sleep(sleep_time)

            # Accept a connection from a client
            cs, address = ss.accept()

            # Create a new thread to handle the client
            client_thread = threading.Thread(
                target=handle_client, args=(cs, address))
            client_thread.start()

    except KeyboardInterrupt:
        print("Server shutting down...")

    finally:
        # Close the server socket
        ss.close()


# Start the server
if __name__ == '__main__':
    main()
