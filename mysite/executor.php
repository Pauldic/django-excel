class ExecAsync {

    public function __construct($cmd) {
        $this->cmd = $cmd;
        $this->cacheFile = ".cache-pipe-".uniqid();
        $this->lineNumber = 0;
    }

    public function getLine() {
        $file = new SplFileObject($this->cacheFile);
        $file->seek($this->lineNumber);
        if($file->valid())
        {
            $this->lineNumber++;
            $current = $file->current();
            return $current;
        } else
            return NULL;
    }

    public function hasFinished() {
        if(file_exists(".status-".$this->cacheFile) ||
            (!file_exists(".status-".$this->cacheFile) && !file_exists($this->cacheFile)))
        {
            unlink($this->cacheFile);
            unlink(".status-".$this->cacheFile);
            $this->lineNumber = 0;
            return TRUE;
        } else
            return FALSE;
    }

    public function run() {
        if($this->cmd) {
            $out = exec('{ '.$this->cmd." > ".$this->cacheFile." && echo finished > .status-".$this->cacheFile.";} > /dev/null 2>/dev/null &");
        }
    }
}

$command = new ExecAsync("git pull  origin master");
$command->run();

while(($line = $command->getLine()) || !$command->hasFinished())
{
    if($line !== NULL)
    {
        echo $line."\n";
        flush();
    } else
    {
        usleep(10);
    }
}