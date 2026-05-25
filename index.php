<?php
$html = __DIR__ . '/index.html';
echo file_exists($html) ? file_get_contents($html) : '<h1>index.html bulunamadı! Aynı klasöre yükleyin.</h1>';