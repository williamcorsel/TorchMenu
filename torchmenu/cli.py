import os
from pathlib import Path


def main():
    filename = Path(__file__).parent / 'Home.py'
    os.system(f'streamlit run {filename}')


if __name__ == '__main__':
    main()
