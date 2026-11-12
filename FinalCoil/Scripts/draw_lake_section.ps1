Add-Type -AssemblyName System.Drawing
$d=Get-Content 'D:/GameDevelop/FinalCoil/Review/TerrainV2/lake_section.json' -Raw | ConvertFrom-Json
$W=1400;$H=650;$L=90;$R=1360;$Top=105;$Bottom=555
$xmax=1330.0;$zmin=-14.0;$zmax=10.0
function PX([double]$x){return [single]($L+$x/$xmax*($R-$L))}
function PY([double]$z){return [single]($Bottom-($z-$zmin)/($zmax-$zmin)*($Bottom-$Top))}
$b=[Drawing.Bitmap]::new($W,$H);$g=[Drawing.Graphics]::FromImage($b)
$g.SmoothingMode=[Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([Drawing.Color]::FromArgb(245,246,241))
$font=[Drawing.Font]::new('Segoe UI',13)
$title=[Drawing.Font]::new('Segoe UI',20,[Drawing.FontStyle]::Bold)
$small=[Drawing.Font]::new('Segoe UI',11)
$ink=[Drawing.Brushes]::DarkSlateGray
$g.DrawString('Берёзовка — разрез озёрной котловины',$title,$ink,70,20)
$g.DrawString('Сечение X = 623,33 м. Высоты по треугольникам поверхности; вертикальный масштаб усилен ≈20×.',$small,$ink,72,62)
$grid=[Drawing.Pen]::new([Drawing.Color]::FromArgb(205,213,205),1)
for($x=0;$x -le 1300;$x+=100){$xx=PX $x;$g.DrawLine($grid,$xx,[single]$Top,$xx,[single]$Bottom);$g.DrawString("$x",$small,$ink,($xx-12),($Bottom+12))}
for($z=-14;$z -le 10;$z+=2){$yy=PY $z;$g.DrawLine($grid,[single]$L,$yy,[single]$R,$yy);$g.DrawString("$z м",$small,$ink,30,($yy-10))}
$terrain=[Collections.Generic.List[Drawing.PointF]]::new()
$terrain.Add([Drawing.PointF]::new((PX 0),$Bottom))
foreach($s in $d.samples){$terrain.Add([Drawing.PointF]::new((PX $s.distance_m),(PY $s.ground_m)))}
$terrain.Add([Drawing.PointF]::new((PX $xmax),$Bottom))
$earth=[Drawing.SolidBrush]::new([Drawing.Color]::FromArgb(165,145,108));$g.FillPolygon($earth,$terrain.ToArray())
$wet=@($d.samples | Where-Object {$_.ground_m -lt -2.5})
$water=[Collections.Generic.List[Drawing.PointF]]::new()
$water.Add([Drawing.PointF]::new((PX $wet[0].distance_m),(PY -2.5)))
$water.Add([Drawing.PointF]::new((PX $wet[-1].distance_m),(PY -2.5)))
for($i=$wet.Count-1;$i -ge 0;$i--){$s=$wet[$i];$water.Add([Drawing.PointF]::new((PX $s.distance_m),(PY $s.ground_m)))}
$blue=[Drawing.SolidBrush]::new([Drawing.Color]::FromArgb(106,181,214));$g.FillPolygon($blue,$water.ToArray())
$line=[Collections.Generic.List[Drawing.PointF]]::new()
foreach($s in $d.samples){$line.Add([Drawing.PointF]::new((PX $s.distance_m),(PY $s.ground_m)))}
$groundpen=[Drawing.Pen]::new([Drawing.Color]::FromArgb(71,82,44),3);$g.DrawLines($groundpen,$line.ToArray())
$waterpen=[Drawing.Pen]::new([Drawing.Color]::FromArgb(25,108,164),3)
$g.DrawLine($waterpen,(PX $wet[0].distance_m),(PY -2.5),(PX $wet[-1].distance_m),(PY -2.5))
$g.DrawString('Пологий доступный берег',$font,$ink,100,140)
$g.DrawString('Отмель: плавное углубление',$font,$ink,195,235)
$g.DrawString('Вода: −2,50 м',$font,[Drawing.Brushes]::DarkBlue,550,285)
$g.DrawString('Дно с коллизией: до 10,5 м под водой',$font,$ink,485,465)
$g.DrawString('Более крутой берег',$font,$ink,1110,145)
$g.DrawString('Расстояние по сечению, м',$font,$ink,565,595)
$b.Save('D:/GameDevelop/FinalCoil/Review/TerrainV2/lake_section.png',[Drawing.Imaging.ImageFormat]::Png)
$g.Dispose();$b.Dispose()

