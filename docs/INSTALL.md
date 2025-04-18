# Instructions for installing the software


Typically, I make my Python software installable packages e.g.: `pip install hgnc-retrieval-utils`.<br>
Since that is beyond the scope of this current iteration, please following the instructions below instead.


## Step 1 - Create Python virtual environment

```shell
python3 -m venv venv
```

## Step 2 - Activate the Python virtual environment


```shell
source venv/bin/activate
```

## Step 3 - Upgrade pip
 

```shell
pip install --upgrade pip 
```


## Step 4 - Install Dependencies

```shell
pip install -r requirements.txt
```


## Step 5 - Clone the code from GitHub

You can execute `git clone` or just download the ZIP.

## Step 6 - Run the main program


```shell
python main.py
```