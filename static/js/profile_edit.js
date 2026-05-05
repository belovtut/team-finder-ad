// Profile edit UX helpers: avatar preview and unsaved changes warning.
(function () {
  document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".profile-edit-form");
    if (!form) return;

    let isDirty = false;

    const markDirty = (e) => {
      if (e && e.target && e.target.closest(".skills-container")) {
        return;
      }
      isDirty = true;
    };

    form.addEventListener("input", markDirty, true);
    form.addEventListener("change", markDirty, true);

    const avatarInput = document.getElementById("id_avatar");
    const avatarImg = document.querySelector(".avatar-preview img");
    if (avatarInput && avatarImg) {
      avatarInput.addEventListener("change", () => {
        if (!avatarInput.files || !avatarInput.files[0]) return;
        const reader = new FileReader();
        reader.onload = (e) => {
          avatarImg.src = e.target.result;
        };
        reader.readAsDataURL(avatarInput.files[0]);
      });
    }

    form.addEventListener("submit", () => {
      isDirty = false;
    });

    window.addEventListener("beforeunload", (e) => {
      if (!isDirty) return;
      e.preventDefault();
      e.returnValue = "";
    });
  });
})();
