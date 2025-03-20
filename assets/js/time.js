function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString("th-TH", { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    document.getElementById("current-time").textContent = timeString;
}

// อัปเดตเวลาทุกวินาที
setInterval(updateTime, 1000);

// เรียกฟังก์ชันครั้งแรกเพื่อให้แสดงผลทันที
updateTime();
