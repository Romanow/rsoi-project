import { HttpModule } from '@nestjs/axios';
import { Module } from '@nestjs/common';
import { AppConfigModule } from '../../config/app/config.module';
import { AppConfigService } from '../../config/app/config.service';
import { AuthController } from './auth.controller';

@Module({
  imports: [
    AppConfigModule,
    HttpModule.registerAsync({
      imports: [AppConfigModule],
      useFactory: async (appConfig: AppConfigService) => ({
        timeout: appConfig.httpTimeout,
        maxRedirects: appConfig.httpMaxDirect,
      }),
      inject: [AppConfigService],
    }),
  ],
  controllers: [AuthController],
})
export class AuthModule {}
