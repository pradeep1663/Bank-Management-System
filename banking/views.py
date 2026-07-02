from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection

# Home Page
def home(request):
    return render(request, 'home.html')

# Signup
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']
        acc_type = request.POST['account_type']
        
        with connection.cursor() as cursor:
            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE user_name=%s", [username])
            if cursor.fetchone():
                messages.error(request, 'Username already exists')
                return render(request, 'signup.html')
            
            # Create user
            cursor.execute(
                "INSERT INTO users(user_name, user_password, user_role) VALUES (%s, %s, %s)",
                [username, password, role]
            )
            
            # Get user_id
            cursor.execute("SELECT user_id FROM users WHERE user_name=%s", [username])
            user_id = cursor.fetchone()[0]
            
            # Create account
            cursor.execute(
                "INSERT INTO accounts(user_id, account_type, account_balance) VALUES (%s, %s, %s)",
                [user_id, acc_type, 500]
            )
        
        messages.success(request, 'Signup successful!')
        return redirect('login')
    
    return render(request, 'signup.html')

# Login
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']
        
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE user_name=%s AND user_password=%s AND user_role=%s",
                [username, password,role]
            )
            user = cursor.fetchone()
            
            if user:
                request.session['user_id'] = user[0]
                request.session['username'] = user[1]
                request.session['role'] = user[3]
                messages.success(request, f'Welcome, {user[1]}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid credentials')
    
    return render(request, 'login.html')

# Dashboard
def dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user_id = request.session['user_id']
    role = request.session['role']
    
    if role == 'customer':
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM accounts WHERE user_id=%s",
                [user_id]
            )
            account = cursor.fetchone()
            
        context = {
    'account': {
        'account_balance': account[2],
        'account_type': account[1]
    }
}
        return render(request, 'customer_dashboard.html', context)
    else:
        return render(request, 'admin_dashboard.html')

# Logout
def logout(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully')
    return redirect('home')

# --- CUSTOMER VIEWS ---

def withdraw(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user_id = request.session['user_id']
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM accounts WHERE user_id=%s", [user_id])
        account = cursor.fetchone()
    
    if request.method == 'POST':
        amount = float(request.POST['amount'])
        
        if amount > account[2]:
            messages.error(request, 'Insufficient balance')
        else:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE accounts SET account_balance = account_balance - %s WHERE user_id=%s",
                    [amount, user_id]
                )
            messages.success(request, f'₹{amount} withdrawn successfully')
            return redirect('dashboard')
    
    context = {'account': {'account_balance': account[2]}}
    return render(request, 'withdraw.html', context)

def deposit(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user_id = request.session['user_id']
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM accounts WHERE user_id=%s", [user_id])
        account = cursor.fetchone()
    
    if request.method == 'POST':
        amount = float(request.POST['amount'])
        
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE accounts SET account_balance = account_balance + %s WHERE user_id=%s",
                [amount, user_id]
            )
        messages.success(request, f'₹{amount} deposited successfully')
        return redirect('dashboard')
    
    context = {'account': {'account_balance': account[2]}}
    return render(request, 'deposit.html', context)

def balance(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user_id = request.session['user_id']
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM accounts WHERE user_id=%s", [user_id])
        account = cursor.fetchone()
    
    context = {
        'account': {
            'account_balance': account[2],
            'account_type': account[1]
        }
    }
    return render(request, 'balance.html', context)

def submit_request(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']

    if request.method == 'POST':
        req_type = request.POST['request_type']

        if req_type == 'loan':
            amount = float(request.POST['amount'])
        else:
            amount = 0

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO requests
                (user_id, req_type, req_amount)
                VALUES (%s, %s, %s)
                """,
                [user_id, req_type, amount]
            )

        messages.success(request, f'{req_type} request submitted successfully')
        return redirect('dashboard')

    return render(request, 'request.html')

# --- ADMIN VIEWS ---

def all_users(request):
    if 'user_id' not in request.session:
        return redirect('login')
    if request.session.get('role') != 'admin':
        return redirect('dashboard')
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
    
    users_list = [
        {'user_id': u[0], 'user_name': u[1], 'user_role': u[3]}
        for u in users
    ]
    
    return render(request, 'all_users.html', {'users': users_list})

def delete_user(request, user_id):
    if 'user_id' not in request.session:
        return redirect('login')
    if request.session.get('role') != 'admin':
        return redirect('dashboard')
    
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM accounts WHERE user_id=%s", [user_id])
        cursor.execute("DELETE FROM requests WHERE user_id=%s", [user_id])
        cursor.execute("DELETE FROM users WHERE user_id=%s", [user_id])
    
    messages.success(request, 'User deleted')
    return redirect('all_users')

def view_requests(request):
    if 'user_id' not in request.session:
        return redirect('login')
    if request.session.get('role') != 'admin':
        return redirect('dashboard')
    
    with connection.cursor() as cursor:
        cursor.execute("""
    SELECT
    r.req_id,
    u.user_name,
    r.req_type,
    r.req_amount,
    r.status
    FROM requests r
    JOIN users u
    ON r.user_id = u.user_id
""")
        requests = cursor.fetchall()
    
    requests_list = [
    {
        'req_id': r[0],
        'user': {'user_name': r[1]},
        'req_type': r[2],
        'req_amount': r[3],
        'status': r[4]
    }
    for r in requests
]
    
    return render(request, 'view_requests.html', {'requests': requests_list})

def approve_request(request, req_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE requests SET status='Approved' WHERE req_id=%s",
            [req_id]
        )

    return redirect('view_requests')

def reject_request(request, req_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE requests SET status='Rejected' WHERE req_id=%s",
            [req_id]
        )

    return redirect('view_requests')

def respond_request(request, req_id):
    if 'user_id' not in request.session:
        return redirect('login')

    if request.session.get('role') != 'admin':
        return redirect('dashboard')

    if request.method == 'POST':
        response_text = request.POST['response_text']

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO response
                (request_id, response_text, response_date)
                VALUES (%s, %s, NOW())
                """,
                [req_id, response_text]
            )

        messages.success(request, 'Response submitted successfully')
        return redirect('view_requests')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT r.req_id,
                   u.user_name,
                   r.req_type,
                   r.req_amount
            FROM requests r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.req_id=%s
        """, [req_id])

        req = cursor.fetchone()

    request_data = {
        'req_id': req[0],
        'user_name': req[1],
        'req_type': req[2],
        'req_amount': req[3]
    }

    return render(
        request,
        'respond_request.html',
        {'request_data': request_data}
    )


def view_responses(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                r.req_type,
                r.req_amount,
                res.response_text,
                res.response_date
            FROM requests r
            JOIN response res
                ON r.req_id = res.request_id
            WHERE r.user_id = %s
        """, [user_id])

        responses = cursor.fetchall()

    response_list = [
        {
            'req_type': r[0],
            'req_amount': r[1],
            'response_text': r[2],
            'response_date': r[3]
        }
        for r in responses
    ]

    return render(
        request,
        'view_responses.html',
        {'responses': response_list}
    )

def search_user(request):

    users = []

    if request.method == 'POST':

        user_id = request.POST['user_id']

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    u.user_id,
                    u.user_name,
                    u.user_role,
                    a.account_type,
                    a.account_balance
                FROM users u
                LEFT JOIN accounts a
                    ON u.user_id = a.user_id
                WHERE u.user_id = %s
            """, [user_id])

            data = cursor.fetchall()

        users = [
            {
                'id': row[0],
                'name': row[1],
                'role': row[2],
                'account_type': row[3],
                'balance': row[4]
            }
            for row in data
        ]

    return render(request, 'search_user.html', {'users': users})