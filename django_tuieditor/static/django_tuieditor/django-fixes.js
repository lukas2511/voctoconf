window.django_tuieditor = {
  initEditor: function (textarea, target) {
    const textareaElement = textarea.style
      ? textarea
      : document.querySelector(textarea);
    textareaElement.style.display = "none";
    const editor = new toastui.Editor({
      el: target.style ? target : document.querySelector(target),
      previewStyle: "vertical",
      height: "500px",
      initialValue: textareaElement.value,
      initialEditType: "wysiwyg",
    });
    editor.on("change", function () {
      textareaElement.value = editor.getMarkdown();
    });
    return editor;
  },
  initViewer: function (target, text, noscript) {
    if (noscript){
      const noscriptElement = noscript.style
        ? noscript
        : document.querySelector(noscript);
      noscriptElement.style.display = "none";
    }
    return new toastui.Editor({
      el: target.style ? target : document.querySelector(target),
      viewer: true,
      initialValue: text,
    });
  },
};
