const form = document.getElementById('sr-form');
const statusText = document.getElementById('status');
const inputPreview = document.getElementById('input-preview');
const outputPreview = document.getElementById('output-preview');
const downloadLink = document.getElementById('download-link');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fileInput = document.getElementById('image-input');
  const scale = document.getElementById('scale').value;
  const tile = document.getElementById('tile').value;

  if (!fileInput.files[0]) {
    statusText.textContent = '请先选择图像文件';
    return;
  }

  const file = fileInput.files[0];
  inputPreview.src = URL.createObjectURL(file);
  outputPreview.src = '';
  downloadLink.classList.add('disabled');

  const formData = new FormData();
  formData.append('file', file);
  formData.append('scale', scale);
  formData.append('tile', tile || '0');

  statusText.textContent = '模型处理中，请稍候（大图会更慢）...';

  try {
    const response = await fetch('/api/super-resolve', {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || '请求失败');

    outputPreview.src = `${data.output_url}?t=${Date.now()}`;
    downloadLink.href = data.download_url;
    downloadLink.classList.remove('disabled');
    statusText.textContent = '超分完成，可预览并下载。';
  } catch (error) {
    statusText.textContent = `处理失败：${error.message}`;
  }
});
