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

  // Forgot Password 2-Step OTP Recovery Controller
  const forgotModal = document.getElementById('forgotModal');
  const openForgotBtn = document.getElementById('openForgotModalBtn');
  const closeForgotBtn = document.getElementById('closeForgotModal');
  const cancelForgotBtn = document.getElementById('cancelForgotBtn');
  const forgotForm = document.getElementById('forgotForm');
  const forgotSubtitle = document.getElementById('forgotSubtitle');
  const forgotStep1 = document.getElementById('forgotStep1');
  const forgotStep2 = document.getElementById('forgotStep2');
  const sendOtpBtn = document.getElementById('sendOtpBtn');
  const backToStep1Btn = document.getElementById('backToStep1Btn');
  const forgotEmailInp = document.getElementById('forgotEmail');
  const forgotOtpInp = document.getElementById('forgotOtp');
  const forgotNewPass = document.getElementById('forgotNewPass');
  const forgotConfirmPass = document.getElementById('forgotConfirmPass');
  const otpNotice = document.getElementById('otpNotice');
  const forgotError = document.getElementById('forgotError');
  const forgotSuccess = document.getElementById('forgotSuccess');

  function resetForgotModalState() {
    if (forgotStep1) forgotStep1.style.display = 'grid';
    if (forgotStep2) forgotStep2.style.display = 'none';
    if (forgotSubtitle) forgotSubtitle.textContent = 'Step 1: Enter your registered MITS credentials.';
    if (forgotError) forgotError.hidden = true;
    if (forgotSuccess) forgotSuccess.hidden = true;
    if (forgotOtpInp) forgotOtpInp.value = '';
    if (forgotNewPass) forgotNewPass.value = '';
    if (forgotConfirmPass) forgotConfirmPass.value = '';
    if (sendOtpBtn) {
      sendOtpBtn.disabled = false;
      sendOtpBtn.innerHTML = '<span>Send 6-Digit Verification Code</span> 📨';
    }
  }

  function openForgotModal() {
    if (!forgotModal) return;
    resetForgotModalState();
    if (forgotEmailInp && emailInp?.value) forgotEmailInp.value = emailInp.value.trim();
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

  // Step 1: Request 6-digit OTP dispatched to institute email inbox
  sendOtpBtn?.addEventListener('click', async () => {
    if (forgotError) forgotError.hidden = true;
    if (forgotSuccess) forgotSuccess.hidden = true;

    const email = forgotEmailInp?.value.trim();
    if (!email) {
      if (forgotError) {
        forgotError.textContent = 'Please enter your registered institute email or roll number.';
        forgotError.hidden = false;
      }
      forgotEmailInp?.focus();
      return;
    }

    try {
      sendOtpBtn.disabled = true;
      sendOtpBtn.innerHTML = '<span>Dispatching OTP to College Inbox...</span> ⏳';

      const res = await apiFetch('/auth/request-otp', {
        method: 'POST',
        body: JSON.stringify({ email })
      });

      // Switch to Step 2
      if (forgotStep1) forgotStep1.style.display = 'none';
      if (forgotStep2) forgotStep2.style.display = 'grid';
      if (forgotSubtitle) forgotSubtitle.textContent = 'Step 2: Enter the 6-digit code sent to your private inbox.';

      if (otpNotice) {
        const errNote = res.email_error ? `<br><span style="color: #fb7185; font-size: 11px;">[Mail Config Error: ${res.email_error}]</span>` : '';
        const demoNote = res.demo_otp ? `<br><strong style="color: #facc15; font-size: 11.5px;">[Demo Mode (SMTP not set on server): Code is ${res.demo_otp}]</strong>` : '';
        otpNotice.innerHTML = `📨 ${res.message || 'Verification code ready!'}${errNote}${demoNote}`;
      }

      // Auto-focus OTP input
      setTimeout(() => forgotOtpInp?.focus(), 150);
    } catch (err) {
      if (forgotError) {
        forgotError.textContent = err.message || 'Failed to dispatch OTP. Please check your credentials.';
        forgotError.hidden = false;
      }
    } finally {
      if (sendOtpBtn) {
        sendOtpBtn.disabled = false;
        sendOtpBtn.innerHTML = '<span>Send 6-Digit Verification Code</span> 📨';
      }
    }
  });

  // Back to Step 1
  backToStep1Btn?.addEventListener('click', () => {
    if (forgotStep1) forgotStep1.style.display = 'grid';
    if (forgotStep2) forgotStep2.style.display = 'none';
    if (forgotSubtitle) forgotSubtitle.textContent = 'Step 1: Enter your registered MITS credentials.';
    if (forgotError) forgotError.hidden = true;
    forgotEmailInp?.focus();
  });

  // Step 2: Validate OTP and Set New Password
  forgotForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (forgotError) forgotError.hidden = true;
    if (forgotSuccess) forgotSuccess.hidden = true;

    const email = forgotEmailInp?.value.trim();
    const otp = forgotOtpInp?.value.trim();
    const newPass = forgotNewPass?.value;
    const confirmPass = forgotConfirmPass?.value;

    if (!email) {
      if (forgotError) {
        forgotError.textContent = 'Institute email or roll number missing.';
        forgotError.hidden = false;
      }
      return;
    }

    if (!otp || otp.length !== 6) {
      if (forgotError) {
        forgotError.textContent = 'Please enter the complete 6-digit verification code from your inbox.';
        forgotError.hidden = false;
      }
      forgotOtpInp?.focus();
      return;
    }

    if (!newPass || newPass.length < 6) {
      if (forgotError) {
        forgotError.textContent = 'Password must be at least 6 characters long.';
        forgotError.hidden = false;
      }
      forgotNewPass?.focus();
      return;
    }

    if (newPass !== confirmPass) {
      if (forgotError) {
        forgotError.textContent = 'Passwords do not match. Please re-enter.';
        forgotError.hidden = false;
      }
      forgotConfirmPass?.focus();
      return;
    }

    try {
      const submitBtn = document.getElementById('submitForgotBtn');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Verifying Code...';
      }

      const res = await apiFetch('/auth/reset-password', {
        method: 'POST',
        body: JSON.stringify({ email, otp, new_password: newPass })
      });

      if (forgotSuccess) {
        forgotSuccess.textContent = res.message || 'Identity verified & password updated successfully! You can now sign in.';
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
      }, 1400);
    } catch (err) {
      if (forgotError) {
        forgotError.textContent = err.message || 'Verification failed. Incorrect OTP or expired code.';
        forgotError.hidden = false;
      }
    } finally {
      const submitBtn = document.getElementById('submitForgotBtn');
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Verify & Set Password ✓';
      }
    }
  });
});
