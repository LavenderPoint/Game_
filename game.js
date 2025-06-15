const canvas = document.getElementById('canvas');
const loading = document.getElementById('loading');

Module = {
    preRun: [],
    postRun: [],
    canvas: canvas,
    print: (text) => console.log(text),
    printErr: (text) => console.error(text),
    setStatus: (text) => {
        if (text === "Running...") {
            loading.style.display = 'none';
        }
    },
    totalDependencies: 0,
    monitorRunDependencies: (left) => {
        this.totalDependencies = Math.max(this.totalDependencies, left);
        Module.setStatus(left ? `Загрузка... (${((this.totalDependencies - left) / this.totalDependencies * 100).toFixed(0)}%)` : '');
    }
};

window.addEventListener('resize', () => {
    canvas.style.width = '';
    canvas.style.height = '';
    canvas.style.width = canvas.offsetWidth + 'px';
    canvas.style.height = (canvas.offsetWidth * 800 / 1200) + 'px';
});

window.addEventListener('load', () => {
    window.dispatchEvent(new Event('resize'));
});

// Mobile controls handler
function handle_mobile_control(direction) {
    Module.ccall('handle_mobile_control', null, ['string'], [direction]);
}
