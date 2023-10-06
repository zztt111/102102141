var btn = document.getElementById("btn");
var imgs = [
  document.getElementById("img1"),
  document.getElementById("img2"),
  document.getElementById("img3"),
  document.getElementById("img4"),
  document.getElementById("img5")
];

btn.onclick = function () {
  var promises = [];
  // 创建一个Promise对象数组
  for (var i = 0; i < imgs.length; i++) {
    var img = imgs[i];
    promises.push(animateDice(img));
  }
  
  // 等待所有Promise对象完成
  Promise.all(promises).then(function () {
    console.log("骰子摇动结束");
  });
};
                      
function animateDice(img) {
  return new Promise(function (resolve) {
    img.src = "./img/x.gif"; // 摇骰子的动态图片
    
    setTimeout(function () {
      var no = Math.ceil(Math.random() * 6); // 随机点数
      img.src = "./img/" + no + ".png"; // 设置骰子图片
      resolve(); // 完成Promise
    }, Math.ceil(1000));
  });
}
