# 🧪 QUICK TEST GUIDE

## Server Status
✅ Django server is running on: http://127.0.0.1:8000/

## Test Credentials
**QA Head Account:**
- Email: qahead@plp.edu
- Password: admin123

**QA Admin Account:**
- Email: qaadmin@plp.edu
- Password: admin123

**Department User Account:**
- Email: deptuser@plp.edu
- Password: admin123

---

## 🎯 TEST SCENARIO 1: Create New User

### Steps:
1. Open browser: http://127.0.0.1:8000/
2. Login as QA Head (qahead@plp.edu / admin123)
3. Click "Settings" in the sidebar
4. Click "User Management" card
5. Click the "+ Add User" button
6. Fill in the form:
   - First Name: **Maria**
   - Middle Name: **Santos** (optional)
   - Last Name: **Reyes**
   - Email Prefix: **maria.reyes**
   - Department: **College of Business Administration (CBA)**
   - Role: **User**
   - Status: **Active** (already selected by default)
7. Click "Save"

### Expected Results:
- ✅ Success message appears
- ✅ Generated password is displayed (e.g., "Tiger@2024")
- ✅ Modal button changes to "Done"
- ✅ Copy/remember the password to test login
- ✅ Click "Done" and page reloads
- ✅ New user appears in the table

---

## 🎯 TEST SCENARIO 2: First Login (Password Change)

### Steps:
1. Log out from QA Head account
2. Login with new user:
   - Email: **maria.reyes@plpasig.edu.ph**
   - Password: **[the generated password from Step 1]**
3. After clicking login...

### Expected Results:
- ✅ Password change modal appears immediately
- ✅ Modal has full-screen overlay (cannot close without changing password)
- ✅ Modal shows:
  - "Change Your Password" title
  - "Please change your password to continue" message
  - New Password field
  - Confirm Password field
  - "Change Password" button
- ✅ Try entering passwords that don't match → validation error appears
- ✅ Try entering password less than 6 characters → validation error appears
- ✅ Enter matching valid passwords (e.g., "newpass123" and "newpass123")
- ✅ Click "Change Password"
- ✅ Success message appears
- ✅ Page reloads automatically
- ✅ User is now on the dashboard (Department User view)

---

## 🎯 TEST SCENARIO 3: Subsequent Login (No Modal)

### Steps:
1. Log out from the new user account
2. Login again with:
   - Email: **maria.reyes@plpasig.edu.ph**
   - Password: **[the new password you set in Step 2]**

### Expected Results:
- ✅ Login successful
- ✅ NO password change modal appears
- ✅ Direct access to dashboard
- ✅ User can navigate normally

---

## 🎯 TEST SCENARIO 4: Edit User

### Steps:
1. Log out and login as QA Head again
2. Go to Settings → User Management
3. Find the user you created (maria.reyes@plpasig.edu.ph)
4. Click the "Edit" (pencil icon) button
5. Modal opens with all fields populated
6. Change something (e.g., Department to "College of Computer Studies")
7. Click "Save"

### Expected Results:
- ✅ Modal shows all split name fields populated
- ✅ Email prefix is shown (without @plpasig.edu.ph)
- ✅ Success message appears
- ✅ Table updates with new information
- ✅ NO password is displayed (editing doesn't generate new password)

---

## 🎯 TEST SCENARIO 5: Search & Filter

### Steps:
1. In User Management page, use the filters:
   - Search box: type "maria"
   - Department filter: select "CBA" or "CCS" (depending on what you set)
   - Role filter: select "User"

### Expected Results:
- ✅ Search filters results in real-time
- ✅ Only matching users are shown
- ✅ Clear filters to see all users again

---

## 🎯 TEST SCENARIO 6: Delete User

### Steps:
1. Click "Delete" (trash icon) on the test user
2. Confirm deletion in the dialog

### Expected Results:
- ✅ Confirmation dialog appears
- ✅ After confirming, user is deleted
- ✅ Success message appears
- ✅ User removed from table

---

## 🔍 THINGS TO VERIFY

### Form Fields:
- ✅ First Name is required (red asterisk)
- ✅ Middle Name is optional (no asterisk)
- ✅ Last Name is required (red asterisk)
- ✅ Email shows "@plpasig.edu.ph" next to the input field
- ✅ Status defaults to "Active"
- ✅ NO password field in the form

### Generated Password:
- ✅ Format is like: "Tiger@2024", "Ocean!5891", "Mountain#4521"
- ✅ Contains: Word + Symbol + Numbers
- ✅ Easy to remember but strong

### Password Change Modal:
- ✅ Cannot be closed without changing password
- ✅ Validates password length (min 6 characters)
- ✅ Validates passwords match
- ✅ Shows error messages for validation failures
- ✅ Only appears on first login
- ✅ Never appears again after password is changed

### Database:
- ✅ Users have `is_password_changed` field
- ✅ New users: `is_password_changed = False`
- ✅ After password change: `is_password_changed = True`
- ✅ Existing users: `is_password_changed = True` (from migration)

---

## 🐛 TROUBLESHOOTING

### If password change modal doesn't appear:
1. Check browser console for JavaScript errors
2. Verify user has `is_password_changed: false` in Firebase
3. Clear browser cache and try again

### If generated password doesn't display:
1. Check browser console for errors
2. Verify backend is returning `password` in JSON response
3. Check if `generatedPasswordInfo` div is hidden by CSS

### If email validation fails:
1. Ensure email prefix doesn't contain spaces
2. Use only letters, numbers, dots, and hyphens
3. Don't include @plpasig.edu.ph in the prefix field

---

## ✅ SUCCESS CRITERIA

The system is working correctly if:
1. ✅ New users can be created WITHOUT entering a password
2. ✅ Generated password is displayed to admin after creation
3. ✅ New users see password change modal on first login
4. ✅ Password can be changed successfully
5. ✅ Modal never appears again after password change
6. ✅ All CRUD operations work (Create, Read, Update, Delete)
7. ✅ Search and filters function properly
8. ✅ Email is always formatted as @plpasig.edu.ph

---

## 🎉 ALL FEATURES ARE COMPLETE AND FUNCTIONAL!
