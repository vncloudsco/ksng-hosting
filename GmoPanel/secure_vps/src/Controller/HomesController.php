<?php
/**
 * Created by PhpStorm.
 * User: quanle
 * Date: 2019-12-31
 * Time: 09:55
 */

namespace App\Controller;
use Google_Client;
use Google_Service_Drive;
use Google_Service_Drive_DriveFile;

class HomesController extends AppController
{
    public function initialize(): void
    {
        parent::initialize();
        
    }

    public function index()
    {
        // Get the API client and construct the service object.
        $client = $this->getClient();
        $service = new Google_Service_Drive($client);

        // Print the names and IDs for up to 10 files.
        $optParams = array(
            'pageSize' => 10,
            'fields' => 'nextPageToken, files(id, name)',
            'mimeType' => 'application/vnd.google-apps.folder',
            'q' => "mimeType='application/vnd.google-apps.folder' and name='backup'"
        );
        $results = $service->files->listFiles($optParams);
        if (count($results->getFiles()) == 0) {
            $file = new Google_Service_Drive_DriveFile();
            $file->setName('backup');
            $file->setMimeType('application/vnd.google-apps.folder');
            $folder = $service->files->create($file);
        } else {
            $folder = $results->getFiles()[0];
        }
        //upload files:
        $fileMetadata = new Google_Service_Drive_DriveFile(
            array(
                'name' => 'anhthe.rar',
                'parents' => [$folder->id]
            )
        );
        $content = file_get_contents(WWW_ROOT.'anhthe.rar');
        $file = $service->files->create($fileMetadata, array(
            'data' => $content,
            'mimeType' => 'application/x-rar-compressed, application/octet-stream',
            'uploadType' => 'multipart',
            'fields' => 'id'));
        printf("File ID: %s\n", $file->id);
        die();
    }

    /**
     * Returns an authorized API client.
     * @return Google_Client the authorized client object
     */
    private function getClient()
    {
        $client = new Google_Client();
        $client->setApplicationName('Google Drive API PHP Quickstart');
        $client->setScopes(Google_Service_Drive::DRIVE);
        $client->setAuthConfig(WWW_ROOT.'credentials.json');
        $client->setAccessType('offline');
        $client->setPrompt('select_account consent');

        // Load previously authorized token from a file, if it exists.
        // The file token.json stores the user's access and refresh tokens, and is
        // created automatically when the authorization flow completes for the first
        // time.
        $tokenPath = WWW_ROOT.'token.json';
        if (file_exists($tokenPath)) {
            $accessToken = json_decode(file_get_contents($tokenPath), true);
            $client->setAccessToken($accessToken);
        }

        // If there is no previous token or it's expired.
        if ($client->isAccessTokenExpired()) {
            // Refresh the token if possible, else fetch a new one.
            if ($client->getRefreshToken()) {
                $client->fetchAccessTokenWithRefreshToken($client->getRefreshToken());
            } else {
                // Request authorization from the user.
                $authUrl = $client->createAuthUrl();
                printf("Open the following link in your browser:\n%s\n", $authUrl);
                print 'Enter verification code: ';
//                $authCode = trim(fgets(STDIN));
                $authCode = trim('4/uwHPgS10nltBjOgOnpDgbhVsgVnJtH2gcw-wvaCl6bfOWj8dHAzGyq4');

                // Exchange authorization code for an access token.
                $accessToken = $client->fetchAccessTokenWithAuthCode($authCode);
                $client->setAccessToken($accessToken);

                // Check to see if there was an error.
                if (array_key_exists('error', $accessToken)) {
                    throw new Exception(join(', ', $accessToken));
                }
            }
            // Save the token to a file.
            if (!file_exists(dirname($tokenPath))) {
                mkdir(dirname($tokenPath), 0700, true);
            }
            file_put_contents($tokenPath, json_encode($client->getAccessToken()));
        }
        return $client;
    }

}