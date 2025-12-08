"""
End-to-End tests for user profile management and new calculation types.
These tests use Playwright to simulate real user interactions.

NOTE: These tests require the fastapi_server fixture to be working.
The server fixture starts a test server on port 5555.
If tests hang, check that:
1. Port 5555 is available
2. test_e2e.db is not locked
3. All dependencies are installed (playwright, uvicorn)
"""
import pytest
from playwright.sync_api import Page, expect
import time

# Mark all tests in this module as E2E tests
pytestmark = pytest.mark.e2e

def test_profile_update_flow(page: Page, base_url: str, test_user_credentials: dict):
    """
    E2E test: Login -> Navigate to Profile -> Update Profile -> Verify Changes
    """
    # Login
    page.goto(f"{base_url}login")
    page.fill('input[name="username"]', test_user_credentials["username"])
    page.fill('input[name="password"]', test_user_credentials["password"])
    page.click('button[type="submit"]')
    
    # Wait for dashboard to load
    page.wait_for_url(f"{base_url}dashboard", timeout=10000)
    
    # Navigate to profile page
    page.goto(f"{base_url}profile")
    page.wait_for_load_state("networkidle")
    
    # Update profile information
    page.fill('input[name="first_name"]', 'UpdatedFirstName')
    page.fill('input[name="last_name"]', 'UpdatedLastName')
    
    # Submit form
    page.click('button[type="submit"]')
    
    # Wait for success message
    expect(page.locator('#successAlert')).to_be_visible(timeout=5000)
    expect(page.locator('#successMessage')).to_contain_text('success', ignore_case=True)
    
    # Verify updated name in header
    expect(page.locator('#layoutUserWelcome')).to_contain_text('UpdatedFirstName', ignore_case=True)

def test_password_change_flow(page: Page, base_url: str, test_user_credentials: dict):
    """
    E2E test: Login -> Change Password -> Re-login with new password
    """
    # Login with original password
    page.goto(f"{base_url}login")
    page.fill('input[name="username"]', test_user_credentials["username"])
    page.fill('input[name="password"]', test_user_credentials["password"])
    page.click('button[type="submit"]')
    
    # Wait for dashboard
    page.wait_for_url(f"{base_url}dashboard", timeout=10000)
    
    # Navigate to change password page
    page.goto(f"{base_url}change-password")
    page.wait_for_load_state("networkidle")
    
    # Fill password form
    new_password = "NewTestPass456"
    page.fill('input[name="current_password"]', test_user_credentials["password"])
    page.fill('input[name="new_password"]', new_password)
    page.fill('input[name="confirm_new_password"]', new_password)
    
    # Submit form
    page.click('button[type="submit"]')
    
    # Wait for success and redirect to login
    expect(page.locator('#successAlert')).to_be_visible(timeout=5000)
    page.wait_for_url(f"{base_url}login", timeout=10000)
    
    # Try to login with new password
    page.fill('input[name="username"]', test_user_credentials["username"])
    page.fill('input[name="password"]', new_password)
    page.click('button[type="submit"]')
    
    # Should successfully reach dashboard
    page.wait_for_url(f"{base_url}dashboard", timeout=10000)
    expect(page.locator('#layoutUserWelcome')).to_be_visible()

def test_password_change_wrong_current(page: Page, base_url: str, test_user_credentials: dict):
    """
    E2E test: Try to change password with wrong current password (negative scenario)
    """
    # Login
    page.goto(f"{base_url}login")
    page.fill('input[name="username"]', test_user_credentials["username"])
    page.fill('input[name="password"]', test_user_credentials["password"])
    page.click('button[type="submit"]')
    
    # Wait for dashboard
    page.wait_for_url(f"{base_url}dashboard", timeout=10000)
    
    # Navigate to change password
    page.goto(f"{base_url}change-password")
    page.wait_for_load_state("networkidle")
    
    # Fill with wrong current password
    page.fill('input[name="current_password"]', "WrongPassword123")
    page.fill('input[name="new_password"]', "NewPass456")
    page.fill('input[name="confirm_new_password"]', "NewPass456")
    
    # Submit
    page.click('button[type="submit"]')
    
    # Should show error
    expect(page.locator('#errorAlert')).to_be_visible(timeout=5000)
    expect(page.locator('#errorMessage')).to_contain_text('incorrect', ignore_case=True)

def test_create_exponentiation_calculation(page: Page, base_url: str, test_user_credentials: dict):
    """
    E2E test: Login -> Create Exponentiation Calculation -> Verify Result
    """
    # Login
    page.goto(f"{base_url}login")
    page.fill('input[name="username"]', test_user_credentials["username"])
    page.fill('input[name="password"]', test_user_credentials["password"])
    page.click('button[type="submit"]')
    
    # Wait for dashboard
    page.wait_for_url(f"{base_url}dashboard", timeout=10000)
    
    # Select exponentiation
    page.select_option('select[name="type"]', 'exponentiation')
    
    # Enter inputs (2^3 = 8)
    page.fill('input[name="inputs"]', '2, 3')
    
    # Submit calculation
    page.click('button[type="submit"]')
    
    # Wait for success message
    expect(page.locator('#successAlert')).to_be_visible(timeout=5000)
    
    # Wait for table to update
    time.sleep(1)
    page.reload()
    page.wait_for_load_state("networkidle")
    
    # Verify calculation appears in table with correct result
    table = page.locator('#calculationsTable')
    expect(table).to_contain_text('exponentiation', ignore_case=True)
    expect(table).to_contain_text('8')

def test_create_modulus_calculation(page: Page, base_url: str, test_user_credentials: dict):
    """
    E2E test: Login -> Create Modulus Calculation -> Verify Result
    """
    # Login
    page.goto(f"{base_url}login")
    page.fill('input[name="username"]', test_user_credentials["username"])
    page.fill('input[name="password"]', test_user_credentials["password"])
    page.click('button[type="submit"]')
    
    # Wait for dashboard
    page.wait_for_url(f"{base_url}dashboard", timeout=10000)
    
    # Select modulus
    page.select_option('select[name="type"]', 'modulus')
    
    # Enter inputs (10 % 3 = 1)
    page.fill('input[name="inputs"]', '10, 3')
    
    # Submit calculation
    page.click('button[type="submit"]')
    
    # Wait for success message
    expect(page.locator('#successAlert')).to_be_visible(timeout=5000)
    
    # Wait for table to update
    time.sleep(1)
    page.reload()
    page.wait_for_load_state("networkidle")
    
    # Verify calculation appears in table
    table = page.locator('#calculationsTable')
    expect(table).to_contain_text('modulus', ignore_case=True)
    expect(table).to_contain_text('1')

def test_profile_navigation_from_dropdown(page: Page, base_url: str, test_user_credentials: dict):
    """
    E2E test: Login -> Click Profile Dropdown -> Navigate to Profile
    """
    # Login
    page.goto(f"{base_url}login")
    page.fill('input[name="username"]', test_user_credentials["username"])
    page.fill('input[name="password"]', test_user_credentials["password"])
    page.click('button[type="submit"]')
    
    # Wait for dashboard
    page.wait_for_url(f"{base_url}dashboard", timeout=10000)
    
    # Click profile dropdown button
    page.click('#profileMenuButton')
    
    # Wait for dropdown menu to appear
    expect(page.locator('#profileDropdownMenu')).to_be_visible()
    
    # Click profile link
    page.click('a[href="/profile"]')
    
    # Should navigate to profile page
    page.wait_for_url(f"{base_url}profile", timeout=10000)
    expect(page.locator('h2')).to_contain_text('Update Profile', ignore_case=True)

def test_password_navigation_from_dropdown(page: Page, base_url: str, test_user_credentials: dict):
    """
    E2E test: Login -> Click Profile Dropdown -> Navigate to Change Password
    """
    # Login
    page.goto(f"{base_url}login")
    page.fill('input[name="username"]', test_user_credentials["username"])
    page.fill('input[name="password"]', test_user_credentials["password"])
    page.click('button[type="submit"]')
    
    # Wait for dashboard
    page.wait_for_url(f"{base_url}dashboard", timeout=10000)
    
    # Click profile dropdown
    page.click('#profileMenuButton')
    
    # Wait for dropdown
    expect(page.locator('#profileDropdownMenu')).to_be_visible()
    
    # Click change password link
    page.click('a[href="/change-password"]')
    
    # Should navigate to change password page
    page.wait_for_url(f"{base_url}change-password", timeout=10000)
    expect(page.locator('h2')).to_contain_text('Change Password', ignore_case=True)

def test_all_calculation_types_available(page: Page, base_url: str, test_user_credentials: dict):
    """
    E2E test: Verify all 9 calculation types are available in dropdown
    """
    # Login
    page.goto(f"{base_url}login")
    page.wait_for_load_state("networkidle")
    
    # Wait for username field to be visible
    page.wait_for_selector('input[name="username"]', timeout=10000)
    
    page.fill('input[name="username"]', test_user_credentials["username"])
    page.fill('input[name="password"]', test_user_credentials["password"])
    page.click('button[type="submit"]')
    
    # Wait for dashboard
    page.wait_for_url(f"{base_url}dashboard", timeout=10000)
    
    # Get all options in the calculation type dropdown
    options = page.locator('select[name="type"] option').all_text_contents()
    
    # Verify all 9 types are present
    assert 'Addition' in str(options)
    assert 'Subtraction' in str(options)
    assert 'Multiplication' in str(options)
    assert 'Division' in str(options)
    assert 'Exponentiation' in str(options)
    assert 'Modulus' in str(options)
    assert 'Minimum' in str(options)
    assert 'Maximum' in str(options)
    assert 'Average' in str(options)
    
    # Should have exactly 9 options
    assert len(options) == 9

def test_profile_update_with_duplicate_username(page: Page, base_url: str, test_user_credentials: dict):
    """
    E2E test: Try to update profile with existing username (negative scenario)
    """
    # First, create another user
    page.goto(f"{base_url}register")
    page.fill('input[name="first_name"]', 'Existing')
    page.fill('input[name="last_name"]', 'User')
    page.fill('input[name="email"]', 'existing@example.com')
    page.fill('input[name="username"]', 'existinguser')
    page.fill('input[name="password"]', 'Password123!')
    page.fill('input[name="confirm_password"]', 'Password123!')
    page.click('button[type="submit"]')
    
    # Wait and then login with test user
    time.sleep(1)
    page.goto(f"{base_url}login")
    page.fill('input[name="username"]', test_user_credentials["username"])
    page.fill('input[name="password"]', test_user_credentials["password"])
    page.click('button[type="submit"]')
    
    # Navigate to profile
    page.wait_for_url(f"{base_url}dashboard", timeout=10000)
    page.goto(f"{base_url}profile")
    page.wait_for_load_state("networkidle")
    
    # Try to update to existing username
    page.fill('input[name="username"]', 'existinguser')
    page.click('button[type="submit"]')
    
    # Should show error
    expect(page.locator('#errorAlert')).to_be_visible(timeout=5000)
    expect(page.locator('#errorMessage')).to_contain_text('already exists', ignore_case=True)


def test_create_minimum_calculation(page: Page, base_url: str, test_user_credentials: dict):
    """
    E2E test: Login -> Create Minimum Calculation -> Verify Result
    """
    # Login
    page.goto(f"{base_url}login")
    page.fill('input[name="username"]', test_user_credentials["username"])
    page.fill('input[name="password"]', test_user_credentials["password"])
    page.click('button[type="submit"]')
    
    # Wait for dashboard
    page.wait_for_url(f"{base_url}dashboard", timeout=10000)
    
    # Select minimum
    page.select_option('select[name="type"]', 'minimum')
    
    # Enter inputs (min(5, 2, 8, 1) = 1)
    page.fill('input[name="inputs"]', '5, 2, 8, 1')
    
    # Submit calculation
    page.click('button[type="submit"]')
    
    # Wait for success message
    expect(page.locator('#successAlert')).to_be_visible(timeout=5000)
    
    # Wait for table to update
    time.sleep(1)
    page.reload()
    page.wait_for_load_state("networkidle")
    
    # Verify calculation appears in table
    table = page.locator('#calculationsTable')
    expect(table).to_contain_text('minimum', ignore_case=True)
    expect(table).to_contain_text('1')


def test_create_maximum_calculation(page: Page, base_url: str, test_user_credentials: dict):
    """
    E2E test: Login -> Create Maximum Calculation -> Verify Result
    """
    # Login
    page.goto(f"{base_url}login")
    page.fill('input[name="username"]', test_user_credentials["username"])
    page.fill('input[name="password"]', test_user_credentials["password"])
    page.click('button[type="submit"]')
    
    # Wait for dashboard
    page.wait_for_url(f"{base_url}dashboard", timeout=10000)
    
    # Select maximum
    page.select_option('select[name="type"]', 'maximum')
    
    # Enter inputs (max(5, 2, 8, 1) = 8)
    page.fill('input[name="inputs"]', '5, 2, 8, 1')
    
    # Submit calculation
    page.click('button[type="submit"]')
    
    # Wait for success message
    expect(page.locator('#successAlert')).to_be_visible(timeout=5000)
    
    # Wait for table to update
    time.sleep(1)
    page.reload()
    page.wait_for_load_state("networkidle")
    
    # Verify calculation appears in table
    table = page.locator('#calculationsTable')
    expect(table).to_contain_text('maximum', ignore_case=True)
    expect(table).to_contain_text('8')


def test_create_average_calculation(page: Page, base_url: str, test_user_credentials: dict):
    """
    E2E test: Login -> Create Average Calculation -> Verify Result
    """
    # Login
    page.goto(f"{base_url}login")
    page.fill('input[name="username"]', test_user_credentials["username"])
    page.fill('input[name="password"]', test_user_credentials["password"])
    page.click('button[type="submit"]')
    
    # Wait for dashboard
    page.wait_for_url(f"{base_url}dashboard", timeout=10000)
    
    # Select average
    page.select_option('select[name="type"]', 'average')
    
    # Enter inputs (avg(10, 20, 30) = 20.0)
    page.fill('input[name="inputs"]', '10, 20, 30')
    
    # Submit calculation
    page.click('button[type="submit"]')
    
    # Wait for success message
    expect(page.locator('#successAlert')).to_be_visible(timeout=5000)
    
    # Wait for table to update
    time.sleep(1)
    page.reload()
    page.wait_for_load_state("networkidle")
    
    # Verify calculation appears in table
    table = page.locator('#calculationsTable')
    expect(table).to_contain_text('average', ignore_case=True)
    expect(table).to_contain_text('20')
