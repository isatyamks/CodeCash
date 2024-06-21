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
        username = session.get('user')  # Assuming session['user'] contains the username
        if username:
            try:
                # Find all users with the given username
                users = users_collection.find({'name': username})
                emails_to_delete = [user['email'] for user in users]  # Collect emails of users to delete
                
                if emails_to_delete:
                    # Delete all users with the collected emails
                    result = users_collection.delete_many({'email': {'$in': emails_to_delete}})
                    if result.deleted_count > 0:
                        session.pop('user', None)  # Remove user from session
                        print(f'{result.deleted_count} users with username {username} deleted successfully.')
                        return redirect(url_for('login'))  # Redirect to login page after successful deletion
                    else:
                        print(f'No users with username {username} were found to delete.')
                else:
                    print(f'No users found with username {username}.')
            except Exception as e:
                print(f'An error occurred while deleting account: {str(e)}')
    return redirect(url_for('settings'))  # Redirect to settings page if deletion fails or no user found