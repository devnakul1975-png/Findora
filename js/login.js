/**
 * SmartCampus Login Controller
 * Handles user sign in, error feedback, and 1-click demo accounts.
 */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('loginForm');
  const emailInp = document.getElementById('email');
  const passInp = document.getElementById('password');
  const errorEl = document.getElementById('formError');

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (errorEl) errorEl.hidden = true;
      const email = emailInp.value.trim();
      const password = passInp.value;

      try {
        const data = await apiFetch('/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email, password })
        });
        setSession(data);
        if (typeof showToast === 'function') {
          showToast('Welcome Back', `Signed in as ${data.user.name}`);
        }
        setTimeout(() => {
          location.href = data.user.role === 'admin' ? 'admin.html' : '../index.html';
        }, 500);
      } catch (err) {
        if (errorEl) {
          errorEl.textContent = err.message;
          errorEl.hidden = false;
        }
      }
    });
  }

  // Quick Demo Buttons
  document.getElementById('demoStudentBtn')?.addEventListener('click', () => {
    if (emailInp) emailInp.value = 'priya.sharma@mitsgwl.ac.in';
    if (passInp) passInp.value = 'mits2026pass';
    form?.requestSubmit();
  });

  document.getElementById('demoFacultyBtn')?.addEventListener('click', () => {
    if (emailInp) emailInp.value = 'r.gupta@mitsgwalior.in';
    if (passInp) passInp.value = 'mits2026pass';
    form?.requestSubmit();
  });

  document.getElementById('demoAdminBtn')?.addEventListener('click', () => {
    if (emailInp) emailInp.value = 'admin@mitsgwl.ac.in';
    if (passInp) passInp.value = 'admin123';
    form?.requestSubmit();
  });

  // Handle unauthorized admin redirection message
  const urlParams = new URLSearchParams(location.search);
  if (urlParams.get('error') === 'unauthorized' || sessionStorage.getItem('adminAccessDenied')) {
    sessionStorage.removeItem('adminAccessDenied');
    if (errorEl) {
      errorEl.textContent = '🔒 Access Denied: Administrator credentials required to access the Admin Panel.';
      errorEl.hidden = false;
    }
  }

  // Forgot Password Recovery Modal Controller
  const forgotModal = document.getElementById('forgotModal');
  const openForgotBtn = document.getElementById('openForgotModalBtn');
  const closeForgotBtn = document.getElementById('closeForgotModal');
  const cancelForgotBtn = document.getElementById('cancelForgotBtn');
  const forgotForm = document.getElementById('forgotForm');
  const forgotEmailInp = document.getElementById('forgotEmail');
  const forgotNewPass = document.getElementById('forgotNewPass');
  const forgotConfirmPass = document.getElementById('forgotConfirmPass');
  const forgotError = document.getElementById('forgotError');
  const forgotSuccess = document.getElementById('forgotSuccess');

  function openForgotModal() {
    if (!forgotModal) return;
    if (forgotEmailInp && emailInp?.value) forgotEmailInp.value = emailInp.value.trim();
    if (forgotError) forgotError.hidden = true;
    if (forgotSuccess) forgotSuccess.hidden = true;
    forgotModal.classList.add('open');
  }

  function closeForgotModal() {
    if (!forgotModal) return;
    forgotModal.classList.remove('open');
  }

  openForgotBtn?.addEventListener('click', openForgotModal);
  closeForgotBtn?.addEventListener('click', closeForgotModal);
  cancelForgotBtn?.addEventListener('click', closeForgotModal);

  forgotModal?.addEventListener('click', (e) => {
    if (e.target === forgotModal) closeForgotModal();
  });

  forgotForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (forgotError) forgotError.hidden = true;
    if (forgotSuccess) forgotSuccess.hidden = true;

    const email = forgotEmailInp?.value.trim();
    const newPass = forgotNewPass?.value;
    const confirmPass = forgotConfirmPass?.value;

    if (!email) {
      if (forgotError) {
        forgotError.textContent = 'Please enter your institute email or roll number.';
        forgotError.hidden = false;
      }
      return;
    }

    if (newPass.length < 6) {
      if (forgotError) {
        forgotError.textContent = 'Password must be at least 6 characters long.';
        forgotError.hidden = false;
      }
      return;
    }

    if (newPass !== confirmPass) {
      if (forgotError) {
        forgotError.textContent = 'Passwords do not match. Please re-enter.';
        forgotError.hidden = false;
      }
      return;
    }

    try {
      const res = await apiFetch('/auth/reset-password', {
        method: 'POST',
        body: JSON.stringify({ email, new_password: newPass })
      });

      if (forgotSuccess) {
        forgotSuccess.textContent = res.message || 'Password updated successfully! You can now sign in.';
        forgotSuccess.hidden = false;
      }

      // Auto-fill into main login form
      if (emailInp) emailInp.value = email;
      if (passInp) passInp.value = newPass;

      setTimeout(() => {
        closeForgotModal();
        if (typeof showToast === 'function') {
          showToast('Password Updated', 'Your credentials were saved. Click Sign In to continue.');
        }
      }, 1200);
    } catch (err) {
      if (forgotError) {
        forgotError.textContent = err.message || 'Failed to update password. Please check your email.';
        forgotError.hidden = false;
      }
    }
  });
});
