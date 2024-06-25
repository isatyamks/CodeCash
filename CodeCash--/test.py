@login_required
def settings():
    if request.method == 'POST':
        action = request.json.get('action')
        if action == 'logout':
            session.pop('user', None)
            flash('You have been logged out.')
            return '', 204
        elif action == 'delete_account':
            users_collection.delete_one({'name': session['user']})
            session.pop('user', None)
            flash('Your account has been deleted.')
            return '', 204
    return render_template('settings.html')













@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    if request.method == 'POST':
        username = session.get('user')  
        if username:
            try:
             
                users = users_collection.find({'name': username})
                emails_to_delete = [user['email'] for user in users]  
                
                if emails_to_delete:
                   
                    result = users_collection.delete_many({'email': {'$in': emails_to_delete}})
                    if result.deleted_count > 0:
                        session.pop('user', None)  
                        print(f'{result.deleted_count} users with username {username} deleted successfully.')
                        return redirect(url_for('login'))  
                    else:
                        print(f'No users with username {username} were found to delete.')
                else:
                    print(f'No users found with username {username}.')
            except Exception as e:
                print(f'An error occurred while deleting account: {str(e)}')
    return redirect(url_for('settings'))  