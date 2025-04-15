# The Usage on Windows

The demonstration is based on Stata-17-MP, and the Stata is installed in `C:\Program Files\Stata17\StataMP-64.exe`
## English Version


## 中文版本
### 确保Stata已经成功注册
1. 打开Stata文件夹路径

> 具体地，你可以右键Stata快捷方式找到对应的路径。
>
> 如 `C:\Program Files\Stata17`
> 
> 此时你可以在终端或者Power Shell进入到这个路径（通过cd命令）
> 
> 如果你发现如下报错：
> ```shell
> PS C:\> cd C:\Program Files\Stata17
> Set-Location : 找不到接受实际参数“Files\Stata17”的位置形式参数。
> 所在位置 行：1 字符：1
> + cd C:\Program Files\Stata17
> ```
> 毫无疑问，你需要在路径上加上英文字符下的双引号，即 `cd "C:\Program Files\Stata17`

2. 注册Stata命令行

> 运行如下代码
> 
> ```shell 
> .StataMP-64.exe /Register
> ```

3. 测试是否注册成功

重新开一个终端，使用 ``



